class InvalidValues(Exception):
        pass


def overlapping(line1, line2):
    try:
        x_axis1 = set(range(min(line1), max(line1)))
        x_axis2 = set(range(min(line2), max(line2)))
        if any([len(x_axis1 & x_axis2), len(x_axis2 & x_axis1)]):
            return True
        return False
    except Exception:
        raise InvalidValues(
            'Invalid params: params can be either list, sets or tuples')
