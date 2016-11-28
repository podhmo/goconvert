from .typeresolver import TypeMappingResolver
from . import minicode
from . import convertor as c
from . import structure as s
from . import langhelpers

"""
interface BuildStrategy:
    get_functioname(Struct, Struct): string
"""


class DefaultStrategy(object):
    def __init__(self, universe):
        self.universe = universe
        self.gencode = None

    def get_convert_name(self, src, dst):
        return "{}To{}".format(langhelpers.titlize(src.name), langhelpers.titlize(dst.name))

    def get_gencode(self):
        if self.gencode is not None:
            return self.gencode
        items = []
        for world in self.universe.worlds.values():
            for module in world.modules.values():
                for file in module.files.values():
                    for alias in file.aliases.values():
                        item = (alias.type_path, alias.fullname)
                        items.append(item)
        self.gencode = minicode.MinicodeGenerator(TypeMappingResolver(items))
        return self.gencode


class ConvertFunctionBuilder(object):
    def __init__(self, universe, module, strategy):
        self.universe = universe
        self.module = module  # output module
        self.strategy = strategy
        self.gencode = strategy.get_gencode()
        self.default_file = self.module.read_file(
            self.module.name, {"name": self.module.name}
        )
        self.convertor = c.ConvertorFromMinicode(c.CoerceMap(self.gencode.resolver))

    def resolve_minicode(self, src_field, dst_field, retry=False):
        try:
            return self.gencode.gencode(src_field.type_path, dst_field.type_path)
        except minicode.TypeToTypeNotResolved as e:
            if retry:
                raise

            # TODO: alias
            src = self.universe.find_definition(e.src_path[-1])
            dst = self.universe.find_definition(e.dst_path[-1])
            if isinstance(src, s.Struct) and isinstance(dst, s.Struct):
                fnname = self.get_functioname(src, dst)
                subfn = self.build(fnname, src, dst)

                def use_subfn(context, value):
                    return subfn(value)
                self.convertor.coerce_map.override(src.pointer.type_path, dst.pointer.type_path, use_subfn)

            return self.resolve_minicode(src_field, dst_field, retry=True)

    def build(self, fnname, src_struct, dst_struct, parent=None):
        # todo: register
        func = s.Function(fnname, parent=parent or self.default_file)
        func.parent.add_function(func.name, func)
        func.add_argument(src_struct.pointer, "src")
        func.add_return_value(dst_struct.pointer)

        dst_struct_type = s.Parameter("", dst_struct, parent=func)
        code_list = []
        for name, dst_field in dst_struct.fields.items():
            if name in src_struct:
                src_field = src_struct.fields[name]
                minicode = self.resolve_minicode(src_field, dst_field)
                code_list.append((src_field, dst_field, minicode))

        @func.write_function
        def write(m, iw):
            with m.func(func.name, func.args, return_=func.returns):
                m.stmt("dst := &{name}{{}}".format(name=dst_struct_type.type_expr))
                for src_field, dst_field, minicode in code_list:
                    value = "src.{}".format(src_field.name)
                    rm, rvalue = self.convertor.code_from_minicode(c.Context(m, iw), minicode, value)
                    rm.stmt("dst.{} = {}".format(dst_field.name, rvalue))
                m.return_("dst")
        return func

    def get_functioname(self, src, dst):
        return self.strategy.get_convert_name(src, dst)
