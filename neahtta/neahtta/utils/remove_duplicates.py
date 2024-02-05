def remove_duplicates(lst, keep_order=False, hashable_elements=True):
    if not keep_order:
        try:
            return list(set(lst))
        except TypeError:
            # unhashable elements of lst
            import warnings

            msg = (
                "remove_duplicates(): unhashable elements, but "
                "`hashable_elements` not explicitly set to False"
            )
            warnings.warn(msg)
            return _remove_duplicates_unhashable_elements(lst)
    else:
        # keep the order, so do it manually
        if hashable_elements:
            return _remove_duplicates_keep_order(lst)
        else:
            return _remove_duplicates_unhashable_elements(lst)


def _remove_duplicates_keep_order(lst):
    seen = set()
    out = []
    for x in lst:
        if x not in seen:
            out.append(x)

            # every element could be of a different type, so we need
            # to check every single one. We cannot just check the first.
            try:
                seen.add(x)
            except TypeError:
                import warnings

                msg = (
                    "remove_duplicates(): unhashable elements, but "
                    "`hashable_elements` not explicitly set to False"
                )
                warnings.warn(msg)
                return _remove_duplicates_unhashable_elements(lst)
    return out


def _remove_duplicates_unhashable_elements(lst):
    # use a list instead of a set when elements are unhashable
    out = []
    for x in lst:
        if x not in out:
            out.append(x)
    return out
