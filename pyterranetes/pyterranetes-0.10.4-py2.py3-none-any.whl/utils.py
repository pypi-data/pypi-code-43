def merge_dicts(*args):
    """Creates a new dict by merging together the values in
``args``. Values to the "right" over ride values in the "left"."""
    if len(args) == 0:
        return {}
    elif len(args) == 1:
        return args[0]
    else:
        args = list(args)
        first = args.pop(0)
        return _merge_dicts(first, merge_dicts(*args))


def _merge_dicts(a, b):
    """Copy values from B into A. destructively modifies A."""

    def rec(a, b):
        for k in b.keys():
            new = b[k]
            if isinstance(new, dict):
                existing = a.get(k, a)
                if existing is a:
                    a[k] = new
                else:
                    if isinstance(existing, dict):
                        rec(existing, new)
                    else:
                        a[k] = new
            else:
                a[k] = new

    rec(a, b)

    return a
