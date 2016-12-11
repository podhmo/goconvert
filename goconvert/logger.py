import sys
import logging


LEVELS = tuple(logging._nameToLevel.keys())


def activate_logger(level="DEBUG", stream=sys.stderr):
    level = getattr(logging, level.upper())
    logging.basicConfig(level=level, stream=stream)
