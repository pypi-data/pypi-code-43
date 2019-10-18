def ensure_list(maybe_iterable):
    if not isinstance(maybe_iterable, list):
        return [maybe_iterable]
    return maybe_iterable
