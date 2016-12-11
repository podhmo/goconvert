import sys  # NOQA
from collections import OrderedDict
from collections import ChainMap
from .langhelpers import titlize
from .langhelpers import reify
from prestring import LazyFormat, LazyArguments


def repr_structure(self):
    fmt = "<{self.__class__.__name__} name={self.name!r} at {id}>"
    return fmt.format(self=self, id=hex(id(self)))


class Universe(object):
    def __init__(self, worlds=None, modules=None, reader=None):
        self.worlds = worlds or OrderedDict()
        self.modules = modules or ChainMap()
        self.reader = reader
        self.nameless = World(self, reader=self.reader)

    def __getitem__(self, name):
        return self.worlds[name]

    def add_world(self, name, world):
        self.worlds[name] = world
        self.modules = self.modules.new_child(world.modules_by_fullname)

    def find_module(self, fullname):
        return self.modules[fullname.rstrip("/")]

    def find_definition(self, fullname):
        if "." not in fullname:
            return Type(fullname)
        module_path, name = fullname.rsplit(".", 1)
        return self.find_module(module_path)[name]

    def create_module(self, name, fullname):
        data = {"name": name, "fullname": fullname, "file": {}}
        return self.nameless.read_module(name, data)


class World(object):
    def __init__(self, parent=None, reader=None):
        self.parent = parent
        self.reader = reader
        self.modules = OrderedDict()

    # TODO: remove it.
    @property
    def modules_by_fullname(self):
        return self.universe.modules

    @property
    def universe(self):
        return self.parent

    def read_module(self, name, module):
        module = self.reader.read_module(module, parent=self)
        fullname = module.fullname
        if fullname in self.modules_by_fullname:
            self.modules_by_fullname[fullname].merge(module)
            result = self.modules[name] = self.modules_by_fullname[fullname]
        else:
            self.modules[name] = module
            result = self.modules_by_fullname[fullname] = self.modules[name]
        return result

    def normalize(self):
        for module in self.modules.values():
            module.normalize()

    def __getitem__(self, name):
        return self.modules[name]


class Module(object):
    def __init__(self, name, fullname, parent=None, reader=None):
        self.name = name
        self.fullname = fullname
        self.parent = parent
        self.reader = reader
        self.files = OrderedDict()
        self.reset()

    __repr__ = repr_structure

    @property
    def package_name(self):
        return self.name

    def merge(self, same):
        self.files.update(same.files)
        self.members.update(same.members)

    def read_file(self, name, file):
        if name in self.files:
            result = self.files[name]
            result.merge(self.reader.read_file(file, parent=self))
        else:
            result = self.files[name] = self.reader.read_file(file, parent=self)
        return result

    def normalize(self):
        self.reset()
        for file in self.files.values():
            file.normalize()
            self.new_child(file.members)

    def reset(self):
        self.members = ChainMap()

    def new_child(self, item):
        self.members = self.members.new_child(item)

    def __getitem__(self, name):
        return self.members[name]

    def get(self, name, default=None):
        return self.members.get(name, default)

    def __contains__(self, name):
        return name in self.members

    @property
    def world(self):
        return self.parent


class File(object):
    def __init__(self, name, imports, parent=None, reader=None):
        self.name = name
        self.imports = imports
        self.parent = parent
        self.reader = reader
        self.aliases = OrderedDict()
        self.structs = OrderedDict()
        self.interfaces = OrderedDict()
        self.functions = OrderedDict()
        self.members = {}

    __repr__ = repr_structure

    def merge(self, other):
        self.aliases.update(other.aliases)
        self.structs.update(other.structs)
        self.interfaces.update(other.interfaces)
        self.functions.update(other.functions)
        self.members.update(other.members)

    @property
    def package_name(self):
        if self.parent is None:
            return None
        return self.parent.package_name

    def normalize(self):
        for struct in self.structs.values():
            struct.normalize()

        for interface in self.interfaces.values():
            interface.normalize()

        for alias in self.aliases.values():
            alias.normalize()

    def read_alias(self, name, alias):
        result = self.members[name] = self.aliases[name] = self.reader.read_alias(alias, parent=self)
        return result

    def read_struct(self, name, struct):
        result = self.members[name] = self.structs[name] = self.reader.read_struct(struct, parent=self)
        return result

    def read_interface(self, name, interface):
        result = self.members[name] = self.interfaces[name] = self.reader.read_interface(interface, parent=self)
        return result

    def read_function(self, name, function):
        result = self.members[name] = self.functions[name] = self.reader.read_function(function, parent=self)
        return result

    def add_function(self, name, function):
        self.members[name] = self.functions[name] = function
        function.parent = self

    def dump(self, writer):
        return writer.write_file(self)

    @property
    def world(self):
        return self.parent.parent

    @property
    def module(self):
        return self.parent


class Type(object):
    def __init__(self, name, fullname=None):
        self.name = name
        self.fullname = fullname or name

    __repr__ = repr_structure

    @reify
    def type_path(self):
        return (self.name, )


class Alias(object):
    def __init__(self, name, data, parent=None, reader=None):
        self.name = name
        self.parent = parent
        self.reader = reader
        self.data = data

    __repr__ = repr_structure

    @reify
    def candidates(self):
        return self.data.get("candidates") or []

    @property
    def package_name(self):
        if self.parent is None:
            return None
        return self.parent.package_name

    @reify
    def type_path(self):
        return tuple(get_type_path(self.data["original"], self))

    @reify
    def type_expr(self):
        return get_type_expr(self.type_path, self)

    def as_pseudo_field(self, field, name):
        return PseudoField(field, name, {"name": name, "type": self.data["original"]}, parent=self, reader=self)

    @reify
    def original_definition(self):
        if "." not in self.type_path[-1]:
            if self.type_path[-1] in self.module:
                return self.module[self.type_path[-1]]
            return Type(self.type_path[-1])
        prefix, name = self.type_path[-1].rsplit(".", 1)
        return self.world.modules_by_fullname[prefix][name]

    @reify
    def fullname(self):
        return get_fulladdress(self.data["name"], self.module)

    def dump(self, writer):
        return writer.write_alias(self)

    def normalize(self):
        pass

    @property
    def world(self):
        return self.parent.parent.parent

    @property
    def module(self):
        return self.parent.parent

    @property
    def file(self):
        return self.parent


class Wrap(object):
    def __init__(self, definition, wrap):
        self.definition = definition
        self.wrap = wrap

    def __repr__(self):
        fmt = "<{self.wrap} {self.definition!r}>"
        return fmt.format(self=self, id=hex(id(self)))

    @reify
    def type_path(self):
        r = [self.wrap]
        r.extend(self.definition.type_path)
        return r

    @reify
    def type_expr(self):
        return get_type_expr(self.type_path, self)

    def __getattr__(self, name):
        return getattr(self.definition, name)


class Struct(object):
    def __init__(self, name, data, parent=None, reader=None):
        self.name = name
        self.parent = parent
        self.reader = reader
        self.data = data
        self.fields = OrderedDict()

    __repr__ = repr_structure

    @reify
    def pointer(self):
        return Wrap(self, "pointer")

    @reify
    def array(self):
        return Wrap(self, "array")

    @property
    def package_name(self):
        if self.parent is None:
            return None
        return self.parent.package_name

    @property
    def fullname(self):
        return get_fulladdress(self.name, self.module)

    @reify
    def type_path(self):
        return [self.fullname]

    @reify
    def type_expr(self):
        return get_type_expr(self.type_path, self)

    def read_field(self, name, field):
        field = self.reader.read_field(field, self)
        self.fields[name.lower()] = field
        return field

    def dump(self, writer):
        return writer.write_struct(self)

    def __getitem__(self, name):
        return self.fields[name]

    def __contains__(self, name):
        return name in self.fields

    def normalize(self):
        pass

    @property
    def world(self):
        return self.parent.parent.parent

    @property
    def module(self):
        return self.parent.parent

    @property
    def file(self):
        return self.parent


class Interface(object):
    def __init__(self, name, data, parent=None, reader=None):
        self.name = name
        self.parent = parent
        self.reader = reader
        self.data = data

    __repr__ = repr_structure

    @property
    def package_name(self):
        if self.parent is None:
            return None
        return self.parent.package_name

    @property
    def fullname(self):
        return get_fulladdress(self.name, self.module)

    @reify
    def type_path(self):
        return [self.fullname]

    def dump(self, writer):
        return writer.write_interface(self)

    def normalize(self):
        pass

    @property
    def world(self):
        return self.parent.parent.parent

    @property
    def module(self):
        return self.parent.parent

    @property
    def file(self):
        return self.parent


def get_type_expr(type_path, container):
    r = []
    last_type = type_path[-1]

    if "." in last_type:
        module_type_path, name = last_type.rsplit(".", 1)
        module = container.world.modules_by_fullname[module_type_path]
        if name in container.module:
            type_path = [*type_path[:-1], name]
        else:
            type_path = [*type_path[:-1], "{}.{}".format(module.name, name)]

    for x in type_path:
        if x == "pointer":
            r.append("*")
        elif x == "array":
            r.append("[]")
        elif "/" in x:
            r.append(x.rsplit("/", 1)[-1])
        else:
            r.append(x)
    return "".join(r)


def get_type_path(value, container):
    if value["kind"] == "primitive":
        module = container.module
        if value["value"] not in module:
            return [value["value"]]
        else:
            return ["{}.{}".format(module.fullname, value["value"])]
    elif value["kind"] == "selector":
        if hasattr(container, "file"):
            container = container.file
        prefix = container.imports[value["prefix"]]["fullname"]
        return ["{}.{}".format(prefix, value["value"])]
    else:
        r = [value["kind"]]
        if "value" in value:
            r.extend(get_type_path(value["value"], container))
        else:
            # interface
            r.append("interface{}")
        return r


def find_module(name, container):
    file = container.file
    module = file.parent
    if module.name == name:
        fullname = module.fullname
    else:
        fullname = file.imports[name]["fullname"]
    return module.parent.modules_by_fullname[fullname]


def get_fulladdress(name, module):
    return "{}.{}".format(module.fullname, name)


class Field(object):
    def __init__(self, name, data, parent=None, reader=None):
        self.name = name
        self.data = data
        self.parent = parent
        self.reader = reader

    __repr__ = repr_structure

    def is_embed(self):
        return self.data.get("embed", False)

    @property
    def type(self):
        return self.data["type"]

    @property
    def tags(self):
        return self.data["tags"]

    @reify
    def type_expr(self):
        return get_type_expr(self.type_path, self)

    @reify
    def suffix(self):
        r = []
        for x in self.type_path:
            if x == "pointer":
                r.append("Ref")
            elif x == "array":
                r.append("Many")
            elif "." in x:
                name = x.rsplit(".", 1)[-1]
                r.append(titlize(name))
            else:
                r.append(x)
        return "".join(reversed(r))

    @reify
    def type_path(self):
        return tuple(get_type_path(self.type, self.parent))

    @reify
    def definition(self):
        if "." not in self.type_path[-1]:
            if self.type_path[-1] in self.module:
                return self.module[self.type_path[-1]]
            return Type(self.type_path[-1])
        prefix, name = self.type_path[-1].rsplit(".", 1)
        return self.world.modules_by_fullname[prefix][name]

    @property
    def world(self):
        return self.parent.parent.parent.parent

    @property
    def module(self):
        return self.parent.parent.parent

    @property
    def file(self):
        return self.parent.parent

    @property
    def struct(self):
        return self.parent


class PseudoField(Field):
    pseudo = True

    def __init__(self, field, *args, **kwargs):
        self.field = field
        super().__init__(*args, **kwargs)


class Function(object):
    def __init__(self, name, parent, body=None, reader=None):
        self.name = name
        self.parent = parent
        self.reader = reader
        self.args = Parameters(parent=self, tmp_prefix="v")
        self.returns = Parameters(parent=self, tmp_prefix="r")
        self.body = body or []
        self.body_fn = None

    __repr__ = repr_structure

    @property
    def world(self):
        return self.parent.world

    @property
    def module(self):
        return self.parent.module

    @property
    def file(self):
        return self.parent

    def add_argument(self, definition, name):
        self.args.add(definition, name)

    def add_return_value(self, definition, name=""):
        self.returns.add(definition, name)

    def write_function(self, fn):
        self.body_fn = fn
        return fn

    def dump(self, writer, iw=None):
        return writer.write_function(self, iw=iw)

    def __call__(self, *args, prefix=None):
        if prefix:
            LazyFormat("{prefix}.{fn}({args})", args=LazyArguments(args), fn=self.name, prefix=prefix)
        else:
            return LazyFormat("{fn}({args})", args=LazyArguments(args), fn=self.name)


class Parameters(object):
    def __init__(self, args_dict=None, parent=None, tmp_prefix="v"):
        self.parent = parent
        self.args_dict = args_dict or OrderedDict()
        self.i = 0
        self.tmp_prefix = tmp_prefix
        self.idx_map = {}

    def __iter__(self):
        return iter(self.args_dict.values())

    def __getitem__(self, k):
        if k in self.idx_map:
            k = self.idx_map[k]
        return self.args_dict[k]

    def __len__(self):
        return len(self.args_dict)

    @property
    def world(self):
        return self.parent.world

    @property
    def module(self):
        return self.parent.module

    @property
    def file(self):
        return self.parent.file

    def add(self, definition, name=""):
        uid = name
        if not uid:
            uid = "{}{}".format(self.tmp_prefix, self.i)
        self.idx_map[self.i] = uid
        self.i += 1
        self.args_dict[uid] = Parameter(name, definition, parent=self)

    def __str__(self):
        return ", ".join(map(str, self.args_dict.values()))


class Parameter(object):
    def __init__(self, name, definition, parent=None):
        self.name = name
        self.definition = definition
        self.parent = parent

    __repr__ = repr_structure

    @property
    def world(self):
        return self.parent.world

    @property
    def module(self):
        return self.parent.module

    @property
    def file(self):
        return self.parent.file

    @reify
    def type_expr(self):
        if isinstance(self.definition, (str, bytes)):
            return self.definition
        else:
            return get_type_expr(self.type_path, self)

    @reify
    def type_path(self):
        if hasattr(self.definition, "type_path"):
            return self.definition.type_path
        else:  # maybe dict
            return get_type_path(self.definition["type"], self)

    def __str__(self):
        if self.name:
            return "{e.name} {e.type_expr}".format(e=self)
        else:
            return "{e.type_expr}".format(e=self)
