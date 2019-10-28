"""
jt_package_name Python package is for Joe Tilsed to have a simple python package template and
upload it onto PyPi. Also available for others to do it themselves.
"""

name = "jt_package_name"


def hello_world():
    """
    Gain the string "Hello World"
    :return:
    "Hello World"
    """
    return "Hello World!"


def hello_user(user):
    """
    Gain the string "Hello <user>" where <user> is what was passed in param
    :param user:
    The users name
    :return:
    "Hello <user>" where <user> is what was passed in param
    """
    return "Hello {}".format(user)


# That's all folks...
