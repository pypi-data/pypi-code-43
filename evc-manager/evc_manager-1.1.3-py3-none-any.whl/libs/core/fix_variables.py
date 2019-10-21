""" Auxiliary functions to guarantee string and integer variables """


def evaluate_str(string, item_name):
    """ Avoid empty or None strings

    :param: string: value to be evaluated
    :param: item_name: name of item to be evaluated
    :return: correct string
    """

    if not string and string != 0:
        raise ValueError("%s cannot be empty" % item_name)

    if not isinstance(string, str):
        try:
            string = str(string)
        except TypeError:
            raise ValueError("%s must be a string" % item_name)

    return string


def evaluate_integer(integer, item_name):
    """ Evaluate if 'integer' provided is a valid integer

    :return:
        Return Integer >= 0 for valid
        Return False for invalid """

    if integer == 0:
        return 0

    if not integer:
        raise ValueError("%s must be an integer" % item_name)

    if not isinstance(integer, int):
        try:
            integer = int(integer)
            return evaluate_integer(integer, 'integer')
        except TypeError:
            raise ValueError("%s must be an integer" % item_name)

    if integer < 0:
        raise ValueError("%s must be >= 0" % item_name)

    return integer
