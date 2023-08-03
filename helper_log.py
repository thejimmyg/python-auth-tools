import sys


def log(*k, **p):
    print(file=sys.stderr, *k, **p)
