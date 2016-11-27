from collections import UserDict
import logging
logger = logging.getLogger(__name__)


# stolen from pyramid
class reify(object):
    def __init__(self, wrapped):
        self.wrapped = wrapped
        try:
            self.__doc__ = wrapped.__doc__
        except:
            pass

    def __get__(self, inst, objtype=None):
        if inst is None:
            return self
        val = self.wrapped(inst)
        setattr(inst, self.wrapped.__name__, val)
        return val


class Gensym(object):
    def __init__(self, value="tmp"):
        self.value = value
        self.i = 0

    def __call__(self):
        self.i += 1
        return "{}{}".format(self.value, self.i)


def titlize(name):
    if not name:
        return name
    return "{}{}".format(name[0].upper(), name[1:])


def untitlize(name):
    if not name:
        return name
    return "{}{}".format(name[0].lower(), name[1:])


class LoggingMap(UserDict):
    def __setitem__(self, k, v):
        logger.debug("access: %s %s", k, v)
        super().__setitem__(k, v)
