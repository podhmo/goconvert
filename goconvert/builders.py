from .typeresolver import TypeMappingResolver
from . import minicode
from . import convertor as c
from . import structure as s
from . import langhelpers
from .langhelpers import reify


class Impl:
    struct = "struct"
    array = "array"
    registration = "registration"
    codegenerator = "codegenerator"


class Registry(object):
    def __init__(self, universe, registry=None):
        self.universe = universe
        self.registry = {}

    def register_implementation(self, name, impl):
        self.registry[name] = impl

    def get_implementation(self, name):
        return self.registry[name]


class CodeGenerator(object):
    impl_type = Impl.codegenerator

    def __init__(self, registry):
        self.registry = registry

        self.registry.register_implementation(self.impl_type, self)  # xxx

    @reify
    def universe(self):
        return self.registry.universe

    @reify
    def gencode(self):
        registration = self.registry.get_implementation(Impl.registration)
        return minicode.MinicodeGenerator(registration.resolver)

    @reify
    def array_builder(self):
        return self.registry.get_implementation(Impl.array)

    @reify
    def struct_builder(self):
        return self.registry.get_implementation(Impl.struct)

    def on_struct_conversion_notfound(self, src, dst, e):
        # TODO: alias
        if isinstance(src, s.Struct) and isinstance(dst, s.Struct):
            fnname = self.get_functioname(src, dst)
            subfn = self.array_builder.build(fnname, src, dst)

            @self.coerce_map.register(src.pointer.type_path, dst.pointer.type_path)
            def use_subfn(context, value):
                return subfn(value)
        else:
            raise NotImplementedError(e)

    def on_array_conversion_notfound(self, src, dst, e):
        # TODO: alias
        if isinstance(src, s.Struct) and isinstance(dst, s.Struct):
            fnname = self.get_functioname(src, dst)
            subfn = self.array_builder.build(fnname, src, dst)

            @self.coerce_map.register(src.pointer.type_path, dst.pointer.type_path)
            def use_subfn(context, value):
                return subfn(value)
        else:
            raise NotImplementedError(e)

    def generate_minicode(self, src_field, dst_field, retry=False):
        try:
            return self.gencode.gencode(src_field.type_path, dst_field.type_path)
        except minicode.ArrayTypeToArrayTypeNotResolved as e:
            if retry:
                raise
            src = self.universe.find_definition(e.src_path[-1])
            dst = self.universe.find_definition(e.dst_path[-1])
            self.on_array_conversion_notfound(src, dst)
        except minicode.TypeToTypeNotResolved as e:
            if retry:
                raise
            src = self.universe.find_definition(e.src_path[-1])
            dst = self.universe.find_definition(e.dst_path[-1])
            self.on_struct_conversion_notfound(src, dst)
        return self.generate_minicode(src_field, dst_field, retry=True)


class CoerceRegistration(object):
    impl_type = Impl.registration

    def __init__(self, registry):
        self.registry = registry

        self.registry.register_implementation(self.impl_type, self)  # xxx

    @reify
    def universe(self):
        return self.registry.universe

    @reify
    def resolver(self):
        items = self.collect_aliases()
        return TypeMappingResolver(items)

    @reify
    def convertor(self):
        self.registry.get_implementation(Impl.codegenerator)
        return c.ConvertorFromMinicode(c.CoerceMap(self.resolver))

    def register(self, src_type, dst_type):
        return self.convertor.coerce_map.as_override(src_type, dst_type)

    def collect_aliases(self):
        items = []
        for world in self.universe.worlds.values():
            for module in world.modules.values():
                for file in module.files.values():
                    for alias in file.aliases.values():
                        item = (alias.type_path, alias.fullname)
                        items.append(item)
        return items

    def collect_functions(self, module):
        triples = []
        for name, maybe_fn in module.members.items():
            if isinstance(maybe_fn, s.Function):
                def call(context, value, fn=maybe_fn, module=module):
                    if fn.module == module:
                        return fn(value)
                    else:
                        context.iw.import_(fn.module)
                        return fn(value, prefix=fn.module)
                item = (maybe_fn.args[0].type_path, maybe_fn.returns[0].type_path, call)
                triples.append(item)
        return triples

    def register_from_module(self, module, skip=lambda fn: fn.file.name.startswith("autogen_")):
        for name, maybe_fn in module.members.items():
            if skip(maybe_fn):
                continue
            if isinstance(maybe_fn, s.Function):
                @self.register(maybe_fn.args[0].type_path, maybe_fn.returns[0].type_path)
                def call(context, value, fn=maybe_fn, module=module):
                    if fn.module == module:
                        return fn(value)
                    else:
                        context.iw.import_(fn.module)
                        return fn(value, prefix=fn.module)


class ArrayConvertDefinition(object):
    impl_type = Impl.array

    def __init__(self, registry, module):
        self.module = module  # output module
        self.registry = registry

        self.registry.register_implementation(self.impl_type, self)  # xxx

    @reify
    def universe(self):
        return self.registry.universe

    @reify
    def struct_builder(self):
        return self.registry.get_implementation(Impl.struct)


class StructConvertDefinition(object):
    impl_type = Impl.struct

    def __init__(self, registry, module):
        self.registry = registry
        self.module = module  # output module
        self.default_file = self.module.read_file(
            self.module.name, {"name": self.module.name}
        )

        self.registry.register_implementation(self.impl_type, self)  # xxx

    @reify
    def universe(self):
        return self.registry.universe

    @reify
    def coerce_map(self):
        return self.registry.get_implementation(Impl.registration)

    @reify
    def convertor(self):
        return self.coerce_map.convertor

    @reify
    def codegenerator(self):
        return self.registry.get_implementation(Impl.codegenerator)

    def get_functioname(self, src, dst):
        return "{}To{}".format(langhelpers.titlize(src.name), langhelpers.titlize(dst.name))

    def build(self, fnname, src_struct, dst_struct, parent=None):
        # todo: register
        func = s.Function(fnname, parent=parent or self.default_file)
        func.parent.add_function(func.name, func)
        func.add_argument(src_struct.pointer, "src")
        func.add_return_value(dst_struct.pointer)

        dst_struct_type = s.Parameter("", dst_struct, parent=func)
        code_list = []
        missing_fields = dict(dst_struct.fields.items())

        def iterate(src_struct, missing_fields):
            for name, dst_field in list(missing_fields.items()):
                if name in src_struct:
                    src_field = src_struct.fields[name]
                    code = self.codegenerator.generate_minicode(src_field, dst_field)
                    code_list.append((src_field, dst_field, code))
                    missing_fields.pop(name)

            # ?alias with embed?

            for src_field in src_struct.fields.values():
                if src_field.is_embed():
                    iterate(src_field.definition, missing_fields)
        iterate(src_struct, missing_fields)

        @func.write_function
        def write(m, iw):
            with m.func(func.name, func.args, return_=func.returns):
                m.stmt("dst := &{name}{{}}".format(name=dst_struct_type.type_expr))
                for src_field, dst_field, code in code_list:
                    value = "src.{}".format(src_field.name)
                    rm, rvalue = self.convertor.code_from_minicode(c.Context(m, iw), code, value)
                    rm.stmt("dst.{} = {}".format(dst_field.name, rvalue))
                for _, dst_field in sorted(missing_fields.items()):
                    m.comment("FIXME: missing {}".format(dst_field.name))
                m.return_("dst")
        return func


def get_convert_registry(universe, module):
    registry = Registry(universe)
    StructConvertDefinition(registry, module)
    ArrayConvertDefinition(registry, module)
    CodeGenerator(registry)
    CoerceRegistration(registry)
    return registry


class ConvertBuilder:
    def __init__(self, universe, module, registry_factory=get_convert_registry):
        self.registry = registry_factory(universe, module)

    def register_from_module(self, module):
        return self.registry.get_implementation(Impl.registration).register_from_module(module)

    def build_struct_convert(self, src, dst, name=None):
        b = self.registry.get_implementation(Impl.struct)
        name = name or b.get_functioname(src, dst)
        return b.build(name, src, dst)
