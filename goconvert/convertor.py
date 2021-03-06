from .typeresolver import _wrap_value
from .langhelpers import Gensym


class CoerceMap(object):
    def __init__(self, resolver):
        self.override_map = {}
        self.resolver = resolver

    def as_override(self, src_type, dst_type):
        def decorator(on_write):
            self.override(src_type, dst_type, on_write)
            return on_write
        return decorator

    def override(self, src_type, dst_type, on_write):
        src_type = _wrap_value(src_type)
        dst_type = _wrap_value(dst_type)
        self.resolver.add_relation(src_type, dst_type)
        self.override_map[(src_type, dst_type)] = on_write

    def __contains__(self, pair):
        return pair in self.override_map

    def __getitem__(self, pair):
        return self.override_map[pair]

    def get(self, pair):
        return self.override_map.get(pair)


class Context(object):
    def __init__(self, m, iw=None):
        self.m = m
        self.iw = iw

    def new_context(self, m=None):
        m = m or self.m
        return self.__class__(m.submodule(newline=False), self.iw)


class ConvertorFromMinicode(object):
    def __init__(self, coerce_map):
        self.coerce_map = coerce_map
        self.gensym = Gensym()

    def coerce(self, context, value, src_type, dst_type):
        pair = (src_type, dst_type)
        if pair in self.coerce_map:
            return self.coerce_map[pair](context, value)
        if isinstance(dst_type, (list, tuple)):
            r = []
            for x in dst_type:
                if x == "pointer":
                    r.append("*")
                elif x == "array":
                    r.append("[]")
                else:
                    r.append(x.rsplit("/", 1)[-1])
            return "({})({})".format("".join(r), value)
        elif "/" in dst_type:
            prefix, name = dst_type.rsplit(".")
            if context.iw:
                new_prefix = context.iw.import_fullname(prefix)  # writing import clause if needed
            return "{}.{}({})".format(new_prefix, name, value)
        else:
            return "{}({})".format(dst_type, value)

    def iterate(self, context, value, src_type, dst_type):
        pair = (src_type, dst_type)
        return self.coerce_map[pair](context, value)

    def code_from_minicode(self, context, code, value):
        need_tmp = False
        # optimization: x -> y; y -> z => z(x)
        coerce_buf = []

        def consume_buf(value):
            if not coerce_buf:
                return value
            value = self.coerce(context, value, *coerce_buf[-1])
            tmp = self.gensym()
            context.m.stmt("{} := {}".format(tmp, value))
            coerce_buf.clear()
            return tmp

        m = context.m

        for i, op in enumerate(code):
            if need_tmp:
                tmp = self.gensym()
                m.stmt("{} := {}".format(tmp, value))
                value = tmp
                need_tmp = False

            if op[0] == "deref":
                value = consume_buf(value)
                with m.if_("{} != nil".format(value)):
                    value = "*({})".format(value)
                    tmp = self.gensym()
                    m.stmt("{} := {}".format(tmp, value))
                    return self.code_from_minicode(context.new_context(), code[i + 1:], tmp)
            elif op[0] == "ref":
                value = consume_buf(value)
                value = "&({})".format(value)
                need_tmp = False
            elif op[0] == "coerce":
                pair = (op[1], op[2])
                if pair not in self.coerce_map:
                    coerce_buf.append((op[1], op[2]))
                    continue
                value = consume_buf(value)
                value = self.coerce(context, value, op[1], op[2])
                need_tmp = True
            elif op[0][0] == "iterate":
                value = consume_buf(value)
                value = self.iterate(context, value, op[1], op[2])
                need_tmp = True
            else:
                value = consume_buf(value)
                raise NotImplementedError(op)
        return m, consume_buf(value)
