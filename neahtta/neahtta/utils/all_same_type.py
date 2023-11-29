def all_same_type(iterable):
    """Returns True if all items of an iterable is of the same type, and
    False otherwise. For an empty iterable, it is considered True that all
    items are of the same type.
    """
    # this function short-circuits, all_entries_same_type() does not
    it = iter(iterable)
    try:
        first = next(it)
    except StopIteration:
        # no first element = empty iterable = "all elements are same type"
        return True

    first_type = type(first)
    return all(type(item) is first_type for item in it)


def all_same_type2(iterable):
    # hm.. 2 type() calls for each item (except the first and last item)
    # also, what if iterable is an iterator already, can't be duplicated..
    from itertools import islice

    return all(
        type(a) is type(b) for a, b in zip(iter(iterable), islice(iterable, 1, None))
    )


def all_entries_same_type(lst):
    """Returns True if all elements of a list are of the same type, and
    False otherwise."""
    return len(set(map(type, lst))) <= 1


if __name__ == "__main__":
    # for the empty iterable, we say that all elements are the same type
    assert all_same_type([])
    assert all_entries_same_type([])
    assert all_same_type2([])

    assert all_same_type([None, None])
    assert all_entries_same_type([None, None])
    assert all_same_type2([None, None])

    # primitive types
    assert all_same_type([1])
    assert all_entries_same_type([1])
    assert all_same_type2([1])

    assert all_same_type(["s", "hey"])
    assert all_entries_same_type(["s", "hey"])

    assert all_same_type([b"s", b"hey"])
    assert all_entries_same_type([b"s", b"hey"])

    # inner types are not checked. here the 2 outer items are lists.
    assert all_same_type([[1, 2], ["1", "2"]])
    assert all_entries_same_type([[1, 2], ["1", "2"]])

    # testing that all_same_type() is short-circuiting
    class Lazylist:
        def __init__(self, lst):
            self.inner = lst

        def __getitem__(self, index):
            item = self.inner[index]
            if callable(item):
                return item()
            else:
                return item

        def __len__(self):
            return len(self.inner)

    n_touched = 0

    def touch():
        global n_touched
        n_touched += 1

    # here we will look at 1 item before realizing that all are not same type
    assert not all_same_type(Lazylist([touch, 1, touch, touch]))
    assert n_touched == 1

    # reset for new test (same test as above, but with all_entries_same_type()
    n_touched = 0
    assert not all_entries_same_type(Lazylist([touch, 1, touch, touch]))
    # all_entries_same_type() is not short-circuiting, so we expect all
    # elements to have been inspected
    assert n_touched == 3, n_touched

    # reset for new test
    n_touched = 0
    assert not all_same_type(Lazylist([touch, touch, 1, touch]))
    # this time, on the 3rd item, we realized that not all elements were not
    # the same
    assert n_touched == 2
