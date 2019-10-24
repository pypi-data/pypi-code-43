class Empty:
    """
    A constant that is Like None, but adding a little more.
    When compared with "==", it negates the bool(other) e.g. [] == Empty, {} == Empty, None == Empty

    When compared with "is", "Empty is Empty" only evaluates to True.
    This feature about "is" is convenient when checking default arguments is used or not.
    you can tell the difference between optional argument not set between arbitrarily set None
    e.g.
    def f(a, b=Empty):
        if b is Empty:
            print('b is not set')
        else:
            print('b is set to: ', b)

    f(1)  -> b is not set
    f(1, 2) -> b is set to: 2
    f(1, None) -> b is set to: None
    """
    def __repr__(self):
        return 'Empty'

    def __bool__(self):
        return False

    def __eq__(self, other):
        return not other


Empty = Empty()
