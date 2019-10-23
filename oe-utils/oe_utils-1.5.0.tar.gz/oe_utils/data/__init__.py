# -*- coding: utf-8 -*-
from deprecated import deprecated


@deprecated(
    version="1.5.0",
    reason="This method is duplicated at oe_utils.search.parse_sort_string.",
)
def parse_sort_string(sort):
    """
    Parse a sort string for use with the db.

    :param: sort: the sort string
    """
    if sort is None:
        return []
    else:
        sort_values = sort.rsplit(",")
        sortlist = []
        for se in sort_values:
            order = "desc" if se[0:1] == "-" else "asc"
            field = se[1:] if se[0:1] in ["-", "+"] else se
            field = field.strip()
            sortlist.append((field, order))
        return sortlist
