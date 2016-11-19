from . import structure


class Reader(object):
    def read_world(self, data, parent=None):
        world = structure.World(parent=parent, reader=self)
        for name, module in data["module"].items():
            world.read_module(name, module)
        return world

    def read_module(self, data, parent=None):
        module = structure.Module(data["name"], data["fullname"], parent=parent, reader=self)
        for name, file in data["file"].items():
            module.read_file(name, file)
        return module

    def read_file(self, data, parent=None):
        file = structure.File(data["name"], data["import"], parent=parent, reader=self)
        for name, alias in data["alias"].items():
            file.read_alias(name, alias)
        for name, struct in data["struct"].items():
            file.read_struct(name, struct)
        for name, interface in data["interface"].items():
            file.read_interface(name, interface)
        return file

    def read_struct(self, data, parent=None):
        struct = structure.Struct(data["name"], data, parent=parent, reader=self)
        for name, field in data["fields"].items():
            struct.read_field(name, field)
        return struct

    def read_interface(self, data, parent=None):
        interface = structure.Interface(data["name"], data, parent=parent, reader=self)
        return interface

    def read_alias(self, data, parent=None):
        alias = structure.Alias(data["name"], data, parent=parent, reader=self)
        return alias

    def read_field(self, data, parent=None):
        field = structure.Field(data["name"], data, parent=parent, reader=self)
        return field
