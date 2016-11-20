from collections import defaultdict
from collections import deque
from collections import namedtuple


Action = namedtuple("Action", "action, src, dst")


def _wrap_value(v):
    if isinstance(v, (tuple, list)):
        return tuple(v)
    else:
        return (v,)


def _unwrap_value(v):
    if not _has_detail(v):
        return v[0]
    else:
        return v


def _has_detail(wv):
    return len(wv) > 1


class TypeMappingResolver(object):
    def __init__(self, items):
        self.primitive_map = defaultdict(list)
        self.detail_map = defaultdict(list)
        self.add_relation_list(items)

    def has_relation(self, k, v):
        return v in self.detail_map.get(k, [])

    def add_relation_list(self, relations):
        for k, v in relations:
            self.add_relation(k, v)

    def add_relation(self, k, v):
        k = _wrap_value(k)
        v = _wrap_value(v)
        self._add_value(k, v)
        self._add_value(v, k)

    def _add_value(self, k, v):
        self.detail_map[k].append(v)
        if _has_detail(k) and "array" not in k and "array" not in v:
            self.primitive_map[k[-1:]].append((k, v))
            self.primitive_map[v[-1:]].append((v, k))

    def resolve(self, src, dst):
        if src == dst:
            return []
        src = _wrap_value(src)
        dst = _wrap_value(dst)
        if src[-1:] == dst[-1:]:
            return self.on_finish([src], [dst])
        else:
            # print("detail_map=", self.detail_map)
            # print("primitive_map=", self.primitive_map)
            src_arrived = set()
            dst_arrived = set()
            result = self.tick_src([src], [dst], src_arrived, dst_arrived, deque(), deque())
            return result

    def on_finish(self, src_hist, dst_hist):
        src_hist.extend(reversed(dst_hist))
        path = src_hist
        coerce_path = []
        for i in range(len(path) - 1):
            if path[i] == path[i + 1]:
                continue
            prev, next_ = path[i], path[i + 1]
            if coerce_path and coerce_path[-1][1] == next_ and coerce_path[-1][2] == prev:
                coerce_path.pop()
                continue
            coerce_path.append(Action(action="coerce", src=prev, dst=next_))
        return coerce_path

    def tick_src(self, src_hist, dst_hist, src_arrived, dst_arrived, src_q, dst_q):
        # print("@S", "src_hist=", src_hist, "dst_hist=", dst_hist, "src_arrived=", src_arrived, "src_q=", src_q, "dst_q=", dst_q)
        if src_hist[-1][-1] == dst_hist[-1][-1]:
            if src_hist[-1] == dst_hist[-1]:
                return self.on_finish(src_hist, dst_hist[:-1])
            else:
                return self.on_finish(src_hist, dst_hist)
        if src_hist[-1] not in src_arrived:
            src_arrived.add(src_hist[-1])
            if src_hist[-1] in self.detail_map:
                for item in self.detail_map[src_hist[-1]]:
                    src_q.append(([*src_hist, item], dst_hist))

            for i in range(1, len(src_hist[-1])):
                k = src_hist[-1][i:]
                if k in self.detail_map:
                    for item in self.detail_map[k]:
                        src_q.append(([*src_hist, k, item], dst_hist))
            k = src_hist[-1][-1:]
            if k in self.primitive_map:
                for items in self.primitive_map[k]:
                    src_q.append(([*src_hist, *items], dst_hist))
        if dst_q:
            src_hist, dst_hist = dst_q.pop()
            return self.tick_dst(src_hist, dst_hist, src_arrived, dst_arrived, src_q, dst_q)
        elif src_q:
            return self.tick_dst(src_hist, dst_hist, src_arrived, dst_arrived, src_q, dst_q)
        else:
            return None

    def tick_dst(self, src_hist, dst_hist, src_arrived, dst_arrived, src_q, dst_q):
        # print("@D", "src_hist=", src_hist, "dst_hist=", dst_hist, "src_arrived=", src_arrived, "src_q=", src_q, "dst_q=", dst_q)
        if src_hist[-1][-1] == dst_hist[-1][-1]:
            if src_hist[-1] == dst_hist[-1]:
                return self.on_finish(src_hist, dst_hist[:-1])
            else:
                return self.on_finish(src_hist, dst_hist)
        if dst_hist[-1] not in dst_arrived:
            dst_arrived.add(dst_hist[-1])
            if dst_hist[-1] in self.detail_map:
                for item in self.detail_map[dst_hist[-1]]:
                    dst_q.append((src_hist, [*dst_hist, item]))

            for i in range(1, len(dst_hist[-1])):
                k = dst_hist[-1][i:]
                if k in self.detail_map:
                    for item in self.detail_map[k]:
                        dst_q.append((src_hist, [*dst_hist, k, item]))
            k = dst_hist[-1][-1:]
            if k in self.primitive_map:
                for items in self.primitive_map[k]:
                    dst_q.append((src_hist, [*dst_hist, *items]))
            return self.tick_src(src_hist, dst_hist, src_arrived, dst_arrived, src_q, dst_q)
        if src_q:
            src_hist, dst_hist = src_q.pop()
            return self.tick_src(src_hist, dst_hist, src_arrived, dst_arrived, src_q, dst_q)
        elif dst_q:
            return self.tick_src(src_hist, dst_hist, src_arrived, dst_arrived, src_q, dst_q)
        else:
            return None
