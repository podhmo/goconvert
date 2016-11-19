from collections import OrderedDict
from collections import ChainMap
from .langhelpers import titlize
from .langhelpers import reify


class Universe(object):
    def __init__(self, worlds=None, modules=None):
        self.worlds = worlds or OrderedDict()
        self.modules = modules or ChainMap()

    def __getitem__(self, name):
        return self.worlds[name]

    def add_world(self, name, world):
        self.worlds[name] = world
        self.modules = self.modules.new_child(world.modules_by_fullname)

    def find_module(self, fullname):
        return self.modules[fullname]


class World(object):
    def __init__(self, parent=None, reader=None):
        self.parent = parent
        self.reader = reader
        self.modules = OrderedDict()
        self.modules_by_fullname = {}

    def read_module(self, name, module):
        module = self.reader.read_module(module, parent=self)
        fullname = module.fullname
        if fullname in self.modules_by_fullname:
            self.modules_by_fullname[fullname].merge(module)
            self.modules[name] = self.modules_by_fullname[fullname]
        else:
            self.modules[name] = module
            self.modules_by_fullname[fullname] = self.modules[name]

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

    @property
    def package_name(self):
        return self.name

    def fulladdress(self, name):
        return "{}.{}".format(self.fullname, name)

    def merge(self, same):
        self.files.update(same.files)
        self.members.update(same.members)

    def read_file(self, name, file):
        self.files[name] = self.reader.read_file(file, parent=self)

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
        self.members = {}

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
        self.members[name] = self.aliases[name] = self.reader.read_alias(alias, parent=self)

    def read_struct(self, name, struct):
        self.members[name] = self.structs[name] = self.reader.read_struct(struct, parent=self)

    def read_interface(self, name, interface):
        self.members[name] = self.interfaces[name] = self.reader.read_interface(interface, parent=self)

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

    def __repr__(self):
        return "<Type {!r}>".format(self.name)


class Alias(object):
    def __init__(self, name, data, parent=None, reader=None):
        self.name = name
        self.parent = parent
        self.reader = reader
        self.data = data

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
        return self.module.fulladdress(self.data["name"])

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


class Pointer(object):
    def __init__(self, definition):
        self.definition = definition

    @reify
    def type_path(self):
        r = ["pointer"]
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

    @reify
    def pointer(self):
        return Pointer(self)

    @property
    def package_name(self):
        if self.parent is None:
            return None
        return self.parent.package_name

    @property
    def fullname(self):
        return self.module.fulladdress(self.name)

    @reify
    def type_path(self):
        return [self.fullname]

    @reify
    def type_expr(self):
        return get_type_expr(self.type_path, self)

    def read_field(self, name, field):
        field = self.reader.read_field(field, self)
        self.fields[name.lower()] = field

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

    @property
    def package_name(self):
        if self.parent is None:
            return None
        return self.parent.package_name

    @property
    def fullname(self):
        return self.module.fulladdress(self.name)

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
        if name in module:
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
        prefix = container.parent.imports[value["prefix"]]["fullname"]
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


class Field(object):
    def __init__(self, name, data, parent=None, reader=None):
        self.name = name
        self.data = data
        self.parent = parent
        self.reader = reader

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
    def __init__(self, name, body=None):
        self.name = name
        self.args = Parameters(tmp_prefix="v")
        self.returns = Parameters(tmp_prefix="r")
        self.body = body or []
        self.body_fn = None

    def add_argument(self, definition, name):
        self.args.add(definition, name)

    def add_returns(self, definition, name=""):
        self.returns.add(definition, name)

    def body_function(self, fn):
        self.body_fn = fn
        return fn

    def dump(self, writer, iw=None):
        return writer.write_function(self, iw=iw)


class Parameters(object):
    def __init__(self, args_dict=None, tmp_prefix="v"):
        self.args_dict = args_dict or OrderedDict()
        self.i = 0
        self.tmp_prefix = tmp_prefix

    def __iter__(self):
        return self.args_dict.values()

    def add(self, definition, name=""):
        uid = name
        if not uid:
            uid = "{}{}".format(self.tmp_prefix, self.i)
            self.i += 1
        self.args_dict[uid] = Parameter(name, definition)

    def __str__(self):
        return ", ".join(map(str, self.args_dict.values()))


class Parameter(object):
    def __init__(self, name, definition):
        self.name = name
        self.definition = definition

    @reify
    def type_expr(self):
        if isinstance(self.definition, (str, bytes)):
            return self.definition
        else:
            return get_type_expr(self.definition.type_path, self.definition)

    def __str__(self):
        if self.name:
            return "{e.name} {e.type_expr}".format(e=self)
        else:
            return "{e.type_expr}".format(e=self)
