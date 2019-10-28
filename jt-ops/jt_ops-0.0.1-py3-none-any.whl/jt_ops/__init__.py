"""
'jt_ops' Python Package for usefull global functions that
Joe Tilsed (https://linkedin.com/in/joetilsed) can use (AND SO CAN YOU!).
"""

name = "jt_ops"


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
