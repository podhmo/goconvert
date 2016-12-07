from . import structure
from .langhelpers import Gensym


class Reader(object):
    def __init__(self, universe=None):
        self.universe = universe or structure.Universe(reader=self)
        self.gensym = Gensym("_")
        assert self.universe.reader

    def read_world(self, data, parent=None):
        parent = parent or self.universe
        world = structure.World(parent=parent, reader=self)
        for name, module in (data.get("module") or []).items():
            world.read_module(name, module)
        world.normalize()
        self.universe.add_world(self.gensym(), world)
        return world

    def read_module(self, data, parent=None):
        module = structure.Module(data["name"], data["fullname"], parent=parent, reader=self)
        for name, file in data["file"].items():
            module.read_file(name, file)
        return module

    def read_file(self, data, parent=None):
        file = structure.File(data["name"], (data.get("import") or {}), parent=parent, reader=self)
        if "alias" in data:
            for name, alias in data["alias"].items():
                file.read_alias(name, alias)
        if "struct" in data:
            for name, struct in data["struct"].items():
                file.read_struct(name, struct)
        if "interface" in data:
            for name, interface in data["interface"].items():
                file.read_interface(name, interface)
        if "function" in data:
            for name, function in data["function"].items():
                file.read_function(name, function)
        return file

    def read_struct(self, data, parent=None):
        struct = structure.Struct(data["name"], data, parent=parent, reader=self)
        for name, field in data["fields"].items():
            struct.read_field(name, field)
        return struct

    def read_function(self, data, parent=None):
        function = structure.Function(data["name"], parent=parent, reader=self)
        for p in data["params"]:
            function.add_argument(p, p["name"])
        for p in data["returns"]:
            function.add_return_value(p, p["name"])
        return function

    def read_interface(self, data, parent=None):
        interface = structure.Interface(data["name"], data, parent=parent, reader=self)
        return interface

    def read_alias(self, data, parent=None):
        alias = structure.Alias(data["name"], data, parent=parent, reader=self)
        return alias

    def read_field(self, data, parent=None):
        field = structure.Field(data["name"], data, parent=parent, reader=self)
        return field
