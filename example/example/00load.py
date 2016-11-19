import argparse
import json
from collections import OrderedDict
from goconvert import Reader
from goconvert import Writer
from prestring.go import GoModule


def run(src_file):
    reader = Reader()
    writer = Writer()
    with open(src_file) as rf:
        world = reader.read_world(json.load(rf, object_pairs_hook=OrderedDict))
        world.normalize()
    m = GoModule()
    m.comment("from: skill.go")
    writer.write_file(world.modules["src"].files["../src/skill.go"], m=m)
    m.comment("from: person.go")
    writer.write_file(world.modules["src"].files["../src/person.go"], m=m)
    print(m)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--src", required=True)
    args = parser.parse_args()
    return run(args.src)

if __name__ == "__main__":
    main()
