"""
Some data manipulation utilities
"""


def flatten(_list):
    return list(sum(_list, []))


def zipNoTruncate(a, b):
    def tup(*bbq):
        return tuple(bbq)

    return map(tup, a, b)
