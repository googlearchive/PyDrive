import random


def CreateRandomFileName():
    hash = random.getrandbits(128)
    return "%032x" % hash