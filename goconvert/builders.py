from .structure import Function
from .structure import Parameter
from . import langhelpers

"""
interface BuildStrategy:
    get_functioname(Struct, Struct): string
"""


class DefaultStrategy(object):
    def get_convert_name(self, src, dst):
        return "{}To{}".format(langhelpers.titlize(src.name), langhelpers.titlize(dst.name))


class ConvertFunctionBuilder(object):
    def __init__(self, universe, module, strategy=DefaultStrategy()):
        self.universe = universe
        self.module = module  # output module
        self.strategy = strategy
        self.default_file = self.module.read_file(
            self.module.name, {"name": self.module.name}
        )

    def build(self, fnname, src_struct, dst_struct, parent=None):
        func = Function(fnname, parent=parent or self.default_file)
        func.add_argument(src_struct.pointer, "src")
        func.add_return_value(dst_struct.pointer)

        dst_struct_type = Parameter("", dst_struct, parent=func)

        @func.write_function
        def write(m, iw):
            with m.func(func.name, func.args, return_=func.returns):
                m.stmt("dst := &{name}{{}}".format(name=dst_struct_type.type_expr))
                m.return_("dst")
        return func

    def get_functioname(self, src, dst):
        return self.strategy.get_convert_name(src, dst)
