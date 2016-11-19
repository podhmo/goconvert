import argparse
import json
from collections import OrderedDict
from goconvert import Reader
from goconvert import Writer
from prestring.go import GoModule

from goconvert import Function
from goconvert.langhelpers import titlize


def build_create_empty_struct_func(struct):
    name = "Empty{}".format(titlize(struct.name))
    func = Function(name)
    func.add_returns(struct)

    @func.body_function
    def write(m, iw):
        m.comment("{fnname} : creates empty {structname}".format(fnname=name, structname=struct.name))
        with m.func(func.name, func.args, return_=func.returns):
            with m.block("value := {struct.name}".format(struct=struct)):
                val_part = m.submodule()

            for field in struct.fields.values():
                if field.definition.fullname == "gopkg.in/mgo.v2/bson.ObjectId":
                    if "pointer" in field.type_path:
                        m.comment("{name} is *bson.ObjectId".format(name=field.name))
                    else:
                        iw.import_fullname("gopkg.in/mgo.v2/bson", as_="bson")
                        val_part.stmt("{name}: bson.NewObjectId(),".format(name=field.name))
            m.return_("value")
    return func


def build_create_struct_func(struct):
    creates_empty_name = "Empty{}".format(titlize(struct.name))
    name = titlize(struct.name)
    func = Function(name)
    func.add_argument("func(value {})".format(struct.pointer.type_expr), "modify")
    func.add_returns(struct.pointer)

    @func.body_function
    def write(m, iw):
        m.comment("{fnname} : creates {structname} with modify function".format(fnname=name, structname=struct.name))
        with m.func(func.name, func.args, return_=func.returns):
            m.stmt("value := {fnname}()".format(fnname=creates_empty_name))
            m.stmt("modify(&value)")
            m.return_("&value")
    return func


def run(src_file):
    reader = Reader()
    with open(src_file) as rf:
        world = reader.read_world(json.load(rf, object_pairs_hook=OrderedDict))
        world.normalize()

    m = GoModule()
    writer = Writer(m)
    with writer.with_import(m) as iw:
        build_create_empty_struct_func(world["src"]["User"]).dump(writer, iw=iw)
        build_create_struct_func(world["src"]["User"]).dump(writer, iw=iw)
        build_create_empty_struct_func(world["src"]["Skill"]).dump(writer, iw=iw)
        build_create_struct_func(world["src"]["Skill"]).dump(writer, iw=iw)
        build_create_empty_struct_func(world["src"]["FacebookAuth"]).dump(writer, iw=iw)
        build_create_struct_func(world["src"]["FacebookAuth"]).dump(writer, iw=iw)
        build_create_empty_struct_func(world["src"]["GoogleAuth"]).dump(writer, iw=iw)
        build_create_struct_func(world["src"]["GoogleAuth"]).dump(writer, iw=iw)
        build_create_empty_struct_func(world["src"]["TwitterAuth"]).dump(writer, iw=iw)
        build_create_struct_func(world["src"]["TwitterAuth"]).dump(writer, iw=iw)
        build_create_empty_struct_func(world["src"]["GithubAuth"]).dump(writer, iw=iw)
        build_create_struct_func(world["src"]["GithubAuth"]).dump(writer, iw=iw)
    print(m)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--src", required=True)
    args = parser.parse_args()
    return run(args.src)

if __name__ == "__main__":
    main()
    # run("../json/src.json")
