import sys
import contextlib
from prestring.go import GoModule


class Writer(object):
    prestring_module = GoModule

    def __init__(self, m=None):
        self.m = m or self.prestring_module()

    def write_file(self, file, m=None, iw=None):
        print("-- write: {} --".format(file.name), file=sys.stderr)
        m = m or self.m

        package_name = file.package_name
        if package_name is not None:
            m.package(package_name)

        with self.with_import(m, iw) as iw:
            for struct in file.structs.values():
                self.write_struct(struct, m=m, iw=iw)
            for alias in file.aliases.values():
                self.write_alias(alias, m=m, iw=iw)
            for function in file.functions.values():
                self.write_function(function, m=m, iw=iw)
        return m

    def write_struct(self, struct, m=None, iw=None):
        m = m or self.m
        self.write_comment(struct.data, m=m, iw=iw)
        with m.type_(struct.name, "struct"):
            for field in struct.fields.values():
                field_definition = field.definition

                if hasattr(field_definition, "module") and struct.module != field_definition.module:
                    iw.import_(field_definition.module)

                self.write_comment(field.data, m=m, iw=iw)
                if field.data["embed"]:
                    m.stmt(field.type_expr)
                else:
                    m.stmt("{} {}".format(field.name, field.type_expr))
                if field.tags:
                    tags = " ".join(['{}:"{}"'.format(tag, ",".join(args)) for tag, args in field.tags.items()])
                    m.insert_after("  `{}`".format(tags))
        return m

    def write_alias(self, alias, m=None, iw=None):
        m = m or self.m
        m.type_alias(alias.name, alias.type_expr)
        if hasattr(alias, "original_definition"):
            original_definition = alias.original_definition
            if hasattr(original_definition, "module"):
                iw.import_(alias.original_definition.module)

        if alias.candidates:
            with m.const_group() as const:
                for c in alias.candidates:
                    self.write_comment(c.data, m=const) or const.comment("{} : a member of {}".format(c["name"], alias["name"]))
                    const("{} {} = {}".format(c["name"], alias["name"], c["value"]))
        return m

    def write_function(self, fn, m=None, iw=None):
        m = m or self.m
        if iw:
            for p in fn.args:
                if hasattr(p.definition, "fullname"):
                    iw.import_(p.definition.module)
            for p in fn.returns:
                if hasattr(p.definition, "fullname"):
                    iw.import_(p.definition.module)
        if fn.body_fn:
            return fn.body_fn(m, iw) or m
        else:
            raise NotImplementedError("write_function")

    def write_comment(self, target, m=None, iw=None):
        m = m or self.m
        if "comment" in target:
            m.comment(target["comment"])
            return m
        else:
            return None

    @contextlib.contextmanager
    def with_import(self, m, iw=None):
        import_part = m.submodule()
        if iw is None:
            with import_part.import_group() as im:
                iw = ImportWriter(im)
        yield iw
        if not iw.used:
            import_part.body.body.clear()


class WriterDispatcher(object):
    def __init__(self):
        self.writers = {}

    def dispatch(self, file):
        if file.name not in self.writers:
            self.writers[file.name] = self.create_writer(file)
        return self.writers[file.name]

    def create_writer(self, file):
        return Writer(GoModule())


class ImportWriter(object):
    def __init__(self, im):
        self.im = im
        self.prefix_map = {}  # fullname -> prefix
        self.name_map = {}  # name -> fullname
        self.used = set()
        self.i = 0

    def _get_prefix(self, module):
        fullname = self.name_map.get(module.name)
        if fullname is None:
            self.name_map[module.name] = module.fullname
            return module.name
        elif fullname == module.fullname:
            return module.name
        else:
            prefix = self.prefix_map.get(module.fullname)
            if prefix is None:
                prefix = self.prefix_map[module.fullname] = "{}{}".format(module.name, self.i)
                self.i += 1
            return prefix

    def import_(self, module, as_=None):
        prefix = as_ or self._get_prefix(module)
        return self.import_fullname(module.fullname, as_=prefix)

    def import_fullname(self, fullname, as_=None):
        if fullname in self.used:
            return as_
        self.used.add(fullname)
        self.im.import_(fullname, as_=as_)
        return as_
