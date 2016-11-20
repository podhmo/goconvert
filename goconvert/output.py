import os.path
import glob
from .structure import File
from .structure import Module
from .writer import WriterDispatcher


class SeparatedOutput(object):
    def __init__(self, dirname, fullname=None, parent=None, gen_prefix="autogen_"):
        self.dirname = dirname
        self.gen_prefix = gen_prefix
        self.module = Module(os.path.basename(dirname), fullname, parent=parent)
        self.dispatcher = WriterDispatcher()
        self.prepared = False

    def new_file(self, file_name):
        fname = "{}{}".format(self.gen_prefix, os.path.basename(file_name))
        return File(fname, {}, parent=self.module)

    def prepare(self):
        self.prepared = True
        os.makedirs(self.dirname, exist_ok=True)
        for f in glob.glob(os.path.join(self.dirname, "{}*.go".format(self.gen_prefix))):
            os.remove(f)

    def write_file(self, file):
        if not self.prepared:
            self.prepare()

        path = os.path.join(self.dirname, file.name)
        with open(path, "w") as wf:
            writer = self.dispatcher.dispatch(file)
            wf.write(str(file.dump(writer)))
