import sys  # NOQA
import argparse
import json
import goconvert
from collections import OrderedDict
from goconvert import Reader
from goconvert import Writer
from prestring.go import GoModule

from goconvert.langhelpers import titlize


def build_create_empty_func(name, struct, new_file):
    func = goconvert.Function(name, parent=new_file)
    func.add_return_value(struct)

    struct_type = goconvert.Parameter("", struct, parent=func)

    @func.write_function
    def write(m, iw):
        m.comment("{fnname} : creates empty {structname}".format(fnname=name, structname=struct.name))
        with m.func(func.name, func.args, return_=func.returns):
            with m.block("value := {name}".format(name=struct_type.type_expr)):
                val_part = m.submodule()

            for field in struct.fields.values():
                if tuple(field.type_path) == ("gopkg.in/mgo.v2/bson.ObjectId",):
                    iw.import_fullname("gopkg.in/mgo.v2/bson", as_="bson")
                    val_part.stmt("{name}: bson.NewObjectId(),".format(name=field.name))
            m.return_("value")
    return func


def build_create_with_modify_func(name, struct, create_empty_func, new_file):
    func = goconvert.Function(name, parent=new_file)

    pointer_type = goconvert.Parameter("", struct.pointer, parent=func)
    func.add_argument("func(value {})".format(pointer_type.type_expr), "modify")
    func.add_return_value(struct.pointer)

    @func.write_function
    def write(m, iw):
        m.comment("{fnname} : creates {structname} with modify function".format(fnname=name, structname=struct.name))
        with m.func(func.name, func.args, return_=func.returns):
            m.stmt("value := {fnname}()".format(fnname=create_empty_func.name))
            m.stmt("modify(&value)")
            m.return_("&value")
    return func


def run(src_file, package_name, src_package):
    reader = Reader()
    with open(src_file) as rf:
        world = reader.read_world(json.load(rf, object_pairs_hook=OrderedDict))
        world.normalize()

    m = GoModule()
    writer = Writer(m)

    module = goconvert.Module(package_name, package_name, parent=world)
    new_file = goconvert.File("{}.go".format(package_name), {}, parent=module)
    for file in world.modules[src_package].files.values():
        for struct in file.structs.values():
            name = "Empty{}".format(titlize(struct.name))
            create_empty_func = build_create_empty_func(name, struct, new_file=new_file)
            new_file.add_function(name, create_empty_func)
            name = titlize(struct.name)
            create_with_modify_func = build_create_with_modify_func(name, struct, create_empty_func, new_file)
            new_file.add_function(name, create_with_modify_func)
    print(new_file.dump(writer))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--src", required=True)
    parser.add_argument("--src-package", required=True)
    parser.add_argument("--package", required=True)
    args = parser.parse_args()
    return run(args.src, args.package, args.src_package)

if __name__ == "__main__":
    main()
    # run("../json/src.json", "testdata", "src")
