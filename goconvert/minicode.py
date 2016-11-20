from .typeresolver import Action


class GencodeMappingNotFound(ValueError):
    def __init__(self, msg, src, dst):
        super().__init__(msg)
        self.src_path = src
        self.dst_path = dst


class MiniCodeNormalizer(object):
    def __init__(self, resolver):
        self.resolver = resolver

    def pre_gencode(self, mapping_path):
        # normalize mapping_path
        # e.g. (coerce (array x) (array y))
        #         -> (coerce (array x) x), (coerce x y), (coerce y (array y))
        # e.g. (coerce (array array x) (array array y))
        #         -> (coerce (array array x) (array x)), (coerce (array x) x), (coerce x y)(coerce y (array y)), (coerce (array y) (array array y))
        unfolded = []
        for action in mapping_path:
            if action[0] != "coerce":
                unfolded.append(action)
                continue

            if self.resolver.has_relation(action[1], action[2]):
                unfolded.append(action)
                continue
            # src transform
            src = action[1]
            i = 0
            sub_indices = [0]
            src_tmp = []
            for x in src:
                i += 1
                if x == "array":
                    if src[sub_indices[-1]] == "array":
                        src_tmp.append(Action(action="coerce", src=src[sub_indices[-1]:], dst=src[i:]))
                    else:
                        src_tmp.append(Action(action="coerce", src=src[sub_indices[-1]:], dst=src[i - 1:]))
                        src_tmp.append(Action(action="coerce", src=src[i - 1:], dst=src[i:]))
                    sub_indices.append(i)

            if len(sub_indices) == 1:
                unfolded.append(action)
                continue
            last_src = src[sub_indices[-1]:]

            # dst transform
            dst = action[2]
            dst_tmp = []
            i = 0
            sub_indices = [0]
            for x in dst:
                i += 1
                if x == "array":
                    if dst[sub_indices[-1]] == "array":
                        dst_tmp.append(Action(action="coerce", dst=dst[sub_indices[-1]:], src=dst[i:]))
                    else:
                        dst_tmp.append(Action(action="coerce", dst=dst[sub_indices[-1]:], src=dst[i - 1:]))
                        dst_tmp.append(Action(action="coerce", dst=dst[i - 1:], src=dst[i:]))
                    sub_indices.append(i)

            # if len(sub_indices) == 1:
            #     raise ValueError("invalid operation {}".format(action))

            first_dst = dst[sub_indices[-1]:]
            unfolded.extend(src_tmp)
            unfolded.append(Action(action="coerce", src=last_src, dst=first_dst))
            unfolded.extend(reversed(dst_tmp))

        r = []
        for ac in unfolded:
            if ac[1] == ac[2]:
                continue
            r.append(ac)
        return r

    def simplify(self, unfolded_code):
        code = []
        for ac in unfolded_code:
            if ac[0] == "ref" and code and code[-1][0] == "deref":
                code.pop()
            elif ac[0] == "array" and code and code[-1][0] == "dearray":
                code.pop()
            else:
                code.append(ac)
        return code

    def post_gencode(self, unfolded_code):
        code = self.simplify(unfolded_code)
        stack = [[]]
        for ac in code:
            if ac[0] == "dearray":
                stack.append(["iterate"])
            elif ac[0] == "array":
                sub_code = stack.pop()
                stack[-1].append(tuple(sub_code))
            else:
                stack[-1].append(ac)
        assert len(stack) == 1
        return stack[0]


class MiniCodeGenerator(object):
    # generating mini language
    # [deref] -> *x
    # [ref] -> &x
    # [coerce, x, y] -> finding alias {original: x} and name is y, -> y(x)

    def __init__(self, resolver):
        self.resolver = resolver
        self.normalizer = MiniCodeNormalizer(resolver)  # xxx

    def gencode(self, src_path, dst_path):
        mapping_path = self.resolver.resolve(src_path, dst_path)
        if mapping_path is None:
            msg = "mapping not found {!r} -> {!r}".format(src_path, dst_path)
            raise GencodeMappingNotFound(msg, src_path, dst_path)
        pre_gencode = self.normalizer.pre_gencode(mapping_path)
        code = self._gencode(pre_gencode)
        post_gencode = self.normalizer.post_gencode(code)
        return post_gencode

    def _gencode(self, mapping_path):
        code = []

        def get_primitive_type(v, prev=None):
            return v[-1]

        for action in mapping_path:
            if self.resolver.has_relation(action.src, action.dst):
                code.append(action)
                continue

            if get_primitive_type(action.src) != get_primitive_type(action.dst):
                code.append(action)
                continue

            for typ in action.src[:-1]:
                if typ == "pointer":
                    code.append(("deref", ))
                elif typ == "array":
                    code.append(("dearray",))
                else:
                    raise ValueError("not implemented: typ={}, path={}".format(typ, action.src))
            itr = reversed(action.dst)
            next(itr)
            for typ in itr:
                if typ == "pointer":
                    code.append(("ref", ))
                elif typ == "array":
                    code.append(("array",))
                else:
                    raise ValueError("not implemented: typ={}, path={}".format(typ, action.dst))
        return code
