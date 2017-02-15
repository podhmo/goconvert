import logging
from .typeresolver import TypeMappingResolver
from . import minicode
from . import convertor as c
from . import structure as s
from . import langhelpers
from .langhelpers import reify
logger = logging.getLogger(__name__)


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


def with_implementation(cls):
    def universe(self):
        return self.registry.universe
    cls.universe = reify(universe)

    def registration(self):
        return self.registry.get_implementation(Impl.registration)
    cls.registration = reify(registration)

    def array_definition(self):
        return self.registry.get_implementation(Impl.array)
    cls.array_definition = reify(array_definition)

    def struct_definition(self):
        return self.registry.get_implementation(Impl.struct)
    cls.struct_definition = reify(struct_definition)

    def codegenerator(self):
        return self.registry.get_implementation(Impl.codegenerator)
    cls.codegenerator = reify(codegenerator)
    return cls


@with_implementation
class CodeGenerator(object):
    impl_type = Impl.codegenerator

    def __init__(self, registry):
        self.registry = registry

        self.registry.register_implementation(self.impl_type, self)  # xxx

    @reify
    def gencode(self):
        return minicode.MinicodeGenerator(self.registration.resolver)

    def on_struct_conversion_notfound(self, src, dst, e):
        if isinstance(src, s.Struct) and isinstance(dst, s.Struct):
            self.registration.resolver.add_relation(src.pointer.type_path, dst.pointer.type_path)  # for recursive type
            fnname = self.struct_definition.get_functionname(src, dst)
            logger.info("start register function %s: %s -> %s", fnname, src.pointer.type_path, dst.pointer.type_path)
            subfn = self.struct_definition.define(fnname, src, dst)
            logger.info("end   register function %s: %s -> %s", fnname, src.pointer.type_path, dst.pointer.type_path)

            @self.registration.register(src.pointer.type_path, dst.pointer.type_path)
            def use_subfn(context, value):
                return subfn(value)
        else:
            raise NotImplementedError(e)

    def on_array_conversion_notfound(self, src, dst, e):
        fnname = self.array_definition.get_functionname(src, dst)
        logger.info("start register function %s: %s -> %s", fnname, e.src_path, e.dst_path)
        subfn = self.array_definition._define(fnname, src, dst, e)
        logger.info("end   register function %s: %s -> %s", fnname, e.src_path, e.dst_path)

        @self.registration.register(e.src_path, e.dst_path)
        def use_subfn(context, value):
            return subfn(value)

    def generate_minicode(self, src_field, dst_field, retry=None):
        try:
            return self.gencode.gencode(src_field.type_path, dst_field.type_path)
        except minicode.ArrayTypeToArrayTypeNotResolved as e:
            if retry and isinstance(retry, e.__class__):
                raise
            retry = e
            src = self.universe.find_definition(e.src_path[-1])
            if isinstance(src, s.Alias):
                src = src.original_definition
                retry = None
            for p in reversed(e.src_path[:-1]):
                src = s.Wrap(src, p)

            dst = self.universe.find_definition(e.dst_path[-1])
            if isinstance(dst, s.Alias):
                dst = dst.original_definition
                retry = None
            for p in reversed(e.dst_path[:-1]):
                dst = s.Wrap(dst, p)

            if src.name.endswith(("32", "64")) or dst.name.endswith(("32", "64")):
                normalized_name_src = src.name.replace("32", "").replace("64", "")
                normalized_name_dst = dst.name.replace("32", "").replace("64", "")
                if normalized_name_src == normalized_name_dst:
                    self.registration.resolver.add_relation(src.type_path, dst.type_path)
                    return self.generate_minicode(src_field, dst_field, retry=None)

            self.on_array_conversion_notfound(src, dst, e)
            return self.generate_minicode(src_field, dst_field, retry=retry)
        except minicode.TypeToTypeNotResolved as e:
            if retry and isinstance(retry, e.__class__):
                raise
            retry = e
            src = self.universe.find_definition(e.src_path[-1])
            if isinstance(src, s.Alias):
                src = src.original_definition

            dst = self.universe.find_definition(e.dst_path[-1])
            if isinstance(dst, s.Alias):
                dst = dst.original_definition

            if src.name.endswith(("32", "64")) or dst.name.endswith(("32", "64")):
                normalized_name_src = src.name.replace("32", "").replace("64", "")
                normalized_name_dst = dst.name.replace("32", "").replace("64", "")
                if normalized_name_src == normalized_name_dst:
                    self.registration.resolver.add_relation(src.type_path, dst.type_path)
                    return self.generate_minicode(src_field, dst_field, retry=e)

            self.on_struct_conversion_notfound(src, dst, e)
            return self.generate_minicode(src_field, dst_field, retry=retry)


@with_implementation
class CoerceRegistration(object):
    impl_type = Impl.registration

    def __init__(self, registry):
        self.registry = registry

        self.registry.register_implementation(self.impl_type, self)  # xxx

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
                @self.register(maybe_fn.args[0].type_path, maybe_fn.returns[0].type_path)
                def call(context, value, fn=maybe_fn, module=module):
                    if fn.module == module:
                        return fn(value)
                    else:
                        context.iw.import_(fn.module)
                        return fn(value, prefix=fn.module)
                item = (maybe_fn.args[0].type_path, maybe_fn.returns[0].type_path, call)
                triples.append(item)
        return triples

    def register_from_module(self, module, skip):
        for name, maybe_fn in module.members.items():
            if skip and skip(maybe_fn):
                continue
            if isinstance(maybe_fn, s.Function):
                if len(maybe_fn.args) == 0 or len(maybe_fn.returns) == 0:
                    continue

                @self.register(maybe_fn.args[0].type_path, maybe_fn.returns[0].type_path)
                def call(context, value, fn=maybe_fn, module=module):
                    if fn.module == module:
                        return fn(value)
                    else:
                        context.iw.import_(fn.module)
                        return fn(value, prefix=fn.module)


@with_implementation
class ArrayConvertDefinition(object):
    impl_type = Impl.array

    def __init__(self, registry, module):
        self.module = module  # output module
        self.registry = registry
        self.default_file = self.module.read_file(
            self.module.name, {"name": self.module.name}
        )
        self.registry.register_implementation(self.impl_type, self)  # xxx
        self.cache = {}

    @reify
    def convertor(self):
        return self.registration.convertor

    def get_functionname(self, src, dst):
        src_part = "{}{}".format(src.name, self.get_suffixname(src))
        dst_part = "{}{}".format(dst.name, self.get_suffixname(dst))
        # return "{}To{}".format(langhelpers.titlize(src_part), langhelpers.titlize(dst_part))
        return "Convert{}".format(langhelpers.titlize(src_part))

    def get_suffix(self, t):
        if t == "pointer":
            return "Ref"
        elif t == "array":
            return "Many"
        else:
            return "Unknown"

    def get_suffixname(self, src):
        if hasattr(src, "wrap"):
            return "{}{}".format(self.get_suffixname(src.definition), self.get_suffix(src.wrap))
        else:
            return ""

    def define(self, fnname, src_array, dst_array, parent=None):
        self.codegenerator.generate_minicode(src_array, dst_array)  # xxx
        k = ":".join(map(str, (src_array.definition.type_path, dst_array.definition.type_path)))
        func = self.cache[k]
        return func

    def _define(self, fnname, src, dst, e, parent=None):
        inner_code = e.inner_code
        k = ":".join(map(str, (e.src_path, e.dst_path)))
        func = self.cache[k] = s.Function(fnname, parent=parent or self.default_file)
        func.parent.add_function(func.name, func)
        func.add_argument(src, "from")
        func.add_return_value(dst)

        dst_array_type = s.Parameter("", dst, parent=func)

        @func.write_function
        def write(m, iw):
            m.comment("{} :".format(func.name))
            with m.func(func.name, func.args, return_=func.returns):
                m.stmt("to := make({name}, len(from))".format(name=dst_array_type.type_expr))
                with m.for_("i := range from"):
                    value = "from[i]"
                    rm, rvalue = self.convertor.code_from_minicode(c.Context(m, iw), inner_code, value)
                    rm.stmt("to[i] = {}".format(rvalue))
                m.return_("to")
        return func


@with_implementation
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
    def convertor(self):
        return self.registration.convertor

    def get_functionname(self, src, dst):
        return "Convert{}".format(langhelpers.titlize(dst.name))
        # return "{}To{}".format(langhelpers.titlize(src.name), langhelpers.titlize(dst.name))

    def define(self, fnname, src_struct, dst_struct, parent=None):
        func = s.Function(fnname, parent=parent or self.default_file)
        func.parent.add_function(func.name, func)
        func.add_argument(src_struct.pointer, "from")
        func.add_return_value(dst_struct.pointer)

        dst_struct_type = s.Parameter("", dst_struct, parent=func)
        code_list = []
        missing_fields = dict(dst_struct.fields.items())

        def iterate(src_struct, missing_fields):
            for name, dst_field in sorted(missing_fields.items()):
                if name in src_struct:
                    src_field = src_struct.fields[name]
                    logger.debug("resolve: %s %s -> %s %s", name, src_field.type_path, name, dst_field.type_path)
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
            m.comment("{} :".format(func.name))
            with m.func(func.name, func.args, return_=func.returns):
                m.stmt("to := &{name}{{}}".format(name=dst_struct_type.type_expr))
                for src_field, dst_field, code in code_list:
                    value = "from.{}".format(src_field.name)
                    rm, rvalue = self.convertor.code_from_minicode(c.Context(m, iw), code, value)
                    rm.stmt("to.{} = {}".format(dst_field.name, rvalue))
                for _, dst_field in sorted(missing_fields.items()):
                    m.comment("FIXME: missing {}".format(dst_field.name))
                m.return_("to")
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

    def register_from_module(self, module, skip=lambda fn: "autogen_" in fn.file.name):
        return self.registry.get_implementation(Impl.registration).register_from_module(module, skip)

    def build_struct_convert(self, src, dst, name=None):
        struct_definition = self.registry.get_implementation(Impl.struct)
        fnname = name or struct_definition.get_functionname(src, dst)
        logger.info("start register function %s: %s -> %s", fnname, src.type_path, dst.type_path)
        func = struct_definition.define(fnname, src, dst)
        logger.info("end   register function %s: %s -> %s", fnname, src.type_path, dst.type_path)
        return func
