# flatten a list, simple timeit() numbers on a tiny list
# for benchmarking.


def list_flat(xs):
    # 0.20
    a = []
    for x in xs:
        a.extend(x)
    return a


def iter_flat(it):
    # 0.06
    # --but, list(this) = 0.86
    for x in it:
        yield from x


# the old code used this trick a lot
# def flatten_sum(xs):
#     # 0.31
#     return sum(xs, [])
