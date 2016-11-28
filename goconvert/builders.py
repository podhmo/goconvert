from .typeresolver import TypeMappingResolver
from .minicode import MinicodeGenerator
from . import convertor as c
from .structure import Function
from .structure import Parameter
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
        self.gencode = MinicodeGenerator(TypeMappingResolver(items))
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

    def build(self, fnname, src_struct, dst_struct, parent=None):
        func = Function(fnname, parent=parent or self.default_file)
        func.add_argument(src_struct.pointer, "src")
        func.add_return_value(dst_struct.pointer)

        dst_struct_type = Parameter("", dst_struct, parent=func)
        code_list = []
        for name, dst_field in dst_struct.fields.items():
            if name in src_struct:
                src_field = src_struct.fields[name]
                minicode = self.gencode.gencode(src_field.type_path, dst_field.type_path)
                code_list.append((src_field, dst_field, minicode))

        # todo: move
        convertor = c.ConvertorFromMinicode(c.CoerceMap(self.gencode.resolver))

        @func.write_function
        def write(m, iw):
            with m.func(func.name, func.args, return_=func.returns):
                m.stmt("dst := &{name}{{}}".format(name=dst_struct_type.type_expr))
                for src_field, dst_field, minicode in code_list:
                    value = "src.{}".format(src_field.name)
                    rm, rvalue = convertor.code_from_minicode(c.Context(m, iw), minicode, value)
                    rm.stmt("dst.{} = {}".format(dst_field.name, rvalue))
                m.return_("dst")
        return func

    def get_functioname(self, src, dst):
        return self.strategy.get_convert_name(src, dst)
