import random
import re

newline_pattern = re.compile(r'[\r\n]')


def CreateRandomFileName():
    hash = random.getrandbits(128)
    return "%032x" % hash


def StripNewlines(string):
    return newline_pattern.sub("", string)
