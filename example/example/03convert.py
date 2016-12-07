import sys  # NOQA
import argparse
import json
from collections import OrderedDict
from prestring.go import GoModule  # NOQA
from goconvert import Reader, Writer
from goconvert import builders
from goconvert import structure


def run(src_file, dst_file, override_file):
    reader = Reader()
    writer = Writer()
    for name, f in [("src", src_file), ("dst", dst_file), ("override", override_file)]:
        with open(f) as rf:
            reader.read_world(json.load(rf, object_pairs_hook=OrderedDict))

    convert_module = reader.universe.create_module("convert", "github.com/podhmo/hmm/example/03convert_output")
    strategy = builders.DefaultStrategy(reader.universe)
    b = builders.ConvertFunctionBuilder(reader.universe, convert_module, strategy)

    for name, maybe_fn in convert_module.members.items():
        if "autogen_" not in maybe_fn.file.name:
            if isinstance(maybe_fn, structure.Function):
                @b.register(maybe_fn.args[0].type_path, maybe_fn.returns[0].type_path)
                def call(context, value, fn=maybe_fn, module=convert_module):
                    if fn.module == module:
                        return fn(value)
                    else:
                        context.iw.import_(fn.module)
                        return fn(value, prefix=fn.module)

    src = reader.universe.find_module("github.com/podhmo/hmm/src")
    dst = reader.universe.find_module("github.com/podhmo/hmm/dst")
    fnname = b.get_functioname(src["FullUser"], dst["FullUser"])
    func = b.build(fnname, src["FullUser"], dst["FullUser"])
    fnname = b.get_functioname(src["User"], dst["FullUser"])
    func = b.build(fnname, src["User"], dst["FullUser"])
    fnname = b.get_functioname(src["FullUser"], dst["User"])
    func = b.build(fnname, src["FullUser"], dst["User"])
    fnname = b.get_functioname(src["User"], dst["User"])
    func = b.build(fnname, src["User"], dst["User"])
    print(func.parent.dump(writer))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--src", required=True)
    parser.add_argument("--dst", required=True)
    parser.add_argument("--override", required=True)
    args = parser.parse_args()
    return run(args.src, args.dst, args.override)

if __name__ == "__main__":
    # main()
    run("../json/src.json", "../json/dst.json", "../json/convert.json")
