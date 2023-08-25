import sys


def helper_log(*k, **p):
    print(file=sys.stderr, *k, **p)
