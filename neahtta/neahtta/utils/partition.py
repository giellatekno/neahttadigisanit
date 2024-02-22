def partition(lst, predicate):
    """Return a tuple of two lists. The first contains all `element`
    in `lst` for which predicate(element) returns True. The other list
    contains all elements which predicate(element) returned False."""
    a, b = [], []

    for element in lst:
        target = a if predicate(element) else b
        target.append(element)

    return a, b


def partition_in_place(lst, predicate):
    """Re-arrange the list `lst` in place, so that every `element` in `lst`
    for which `predicate(element)` returns True comes before every element for
    which `predicate(element)` returns False. Relative ordering is _not_
    preserved. Returns the number of elements for which predicate(element)
    returned True. Note that in the case where there is only one element, this
    means that the returned number can be 1, without anything actually being
    moved.
    """
    L = len(lst)

    if L == 0:
        return 0
    if L == 1:
        return int(predicate(lst[0]))

    i = -1
    j = L
    n = 0

    while True:
        while True:
            i += 1
            if i >= j:
                return n
            if not predicate(lst[i]):
                break

        while True:
            j -= 1
            if j <= i:
                return n
            if predicate(lst[j]):
                break

        n += 1
        lst[i], lst[j] = lst[j], lst[i]


def partition_in_place_stable(lst, predicate):
    """Same as partition_in_place, but maintain relative ordering."""
    # anders: I may need this if the re-ordering done with
    # partition_in_place() in morphology/morphology.py breaks
    # some other ordering that some previous code made!
    raise NotImplementedError()

    L = len(lst)

    if L == 0:
        return 0
    if L == 1:
        return int(predicate(lst[0]))

    # ...


if __name__ == "__main__":

    def test_partition1():
        inp = []
        a, b = partition(inp, lambda _: None)
        assert len(a) == 0
        assert len(b) == 0

    def test_partition2():
        inp = [1, 2, 3, 4, 5, 6, 7, 8]
        a, b = partition(inp, lambda x: x % 2 == 0)
        assert a == [2, 4, 6, 8]
        assert b == [1, 3, 5, 7]

    def test_partition3():
        inp = [1, 2, 3, 4, 5, 6, 7, 8]
        a, b = partition(inp, lambda x: x <= 4)
        assert a == [1, 2, 3, 4]
        assert b == [5, 6, 7, 8]

    def test_partition():
        test_partition1()
        test_partition2()
        test_partition3()

    def test_partition_in_place1():
        a = []
        n = partition_in_place(a, lambda _: None)
        assert n == 0

    def test_partition_in_place2():
        inp = [1, 2, 3, 4, 5, 6, 7, 8]
        partition_in_place(inp, lambda x: x % 2 == 0)
        for i in inp[0:4]:
            assert i % 2 == 0
        for i in inp[4:8]:
            assert i % 2 != 0

    def test_partition_in_place3():
        inp = [("a", 0), ("b", 1), (None, 0), ("c", 3), ("d", 4), (None, 0)]
        partition_in_place(inp, lambda tup: isinstance(tup[0], str))
        for a, b in inp[0:4]:
            assert isinstance(a, str)
        for a, b in inp[4:6]:
            assert a is None

    def test_partition_in_place():
        test_partition_in_place1()
        test_partition_in_place2()
        test_partition_in_place3()

    def run_test(test_fn):
        fname = test_fn.__name__[5:]
        print(f"Running units test for {fname}...", end="")
        test_fn()
        print("OK")

    run_test(test_partition)
    run_test(test_partition_in_place)
