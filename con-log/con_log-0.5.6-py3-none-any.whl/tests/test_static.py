from conlog import Conlog


def test_console_dir():

    conlog = Conlog(__name__,  Conlog.DEBUG, enabled=True)

    my_dict = {'name':'Jack', 'age': 26}

    conlog.dir(my_dict)