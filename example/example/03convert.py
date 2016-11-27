import sys  # NOQA
import argparse
import json
from collections import OrderedDict
from goconvert import Reader, Writer
from goconvert import structure
from prestring.go import GoModule  # NOQA
from goconvert import builders


def run(src_file, dst_file):
    reader = Reader()
    writer = Writer()
    for name, f in [("src", src_file), ("dst", dst_file)]:
        with open(f) as rf:
            reader.read_world(json.load(rf, object_pairs_hook=OrderedDict))

    convert_module = reader.universe.create_module("convert", "github.com/podhmo/hmm/convert")
    b = builders.ConvertFunctionBuilder(reader.universe, convert_module)

    src = reader.universe.find_module("github.com/podhmo/hmm/src")
    dst = reader.universe.find_module("github.com/podhmo/hmm/dst")

    fnname = b.get_functioname(src["User"], dst["User"])
    func = b.build(fnname, src["User"], dst["User"])
    print(func.dump(writer))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--src", required=True)
    parser.add_argument("--dst", required=True)
    args = parser.parse_args()
    return run(args.src, args.dst)

if __name__ == "__main__":
    # main()
    run("../json/src.json", "../json/dst.json")