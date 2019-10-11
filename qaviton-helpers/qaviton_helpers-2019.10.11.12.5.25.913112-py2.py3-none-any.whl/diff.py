def list_diff(list1, list2):
    """get the outer-section between lists
    example:
        a = ['a','b','c']
        b = ['a','b']
        list_diff(a, b)
        >['c']
    """
    s = set(list2)
    return [x for x in list1 if x not in s]
