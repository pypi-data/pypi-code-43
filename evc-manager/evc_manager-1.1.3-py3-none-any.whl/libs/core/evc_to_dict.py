""" Module to convert a class to a dictionary """


def convert_class(cls):
    """
        This function is used to convert the models to
        to a dictionary that can be converted to YAML later. \

        This funcion works in a recursive way. So far, each
        class can have three main types:

        value: it is a class that has an int/str/dict/empty_list attribute
            meaning it is 'terminal'
        list: it is a non-empty list
        class: it is another class

        For value, it returns the attribute
        For list, it circulates the list
        For class, it uses vars to identify all attributes and calls
            the convert_class in a recursive way, until reaching
            its value

        :param: cls: class to be converted to dict
        :return: value, a list or a dict
    """

    my_dict = dict()
    if isinstance(cls, (int, str)) or (isinstance(cls, list) and not len(cls)):
        return cls

    elif isinstance(cls, dict):
        return cls

    elif hasattr(cls, '__class__') or isinstance(cls, list):

        if isinstance(cls, list) and len(cls) > 0:
            my_list = list()
            for cl in cls:
                my_list.append(convert_class(cl))
            return my_list

        elif isinstance(cls, list):
            return cls

        else:
            try:
                cvars = vars(cls)
                for var in cvars:
                    if var.startswith('_') and not var.startswith('__'):
                        subcls = getattr(cls, var)
                        my_dict[var[1:]] = convert_class(subcls)
            except TypeError as error:
                print(error)
                print(cls)
                print(type(cls))
                raise TypeError(error)

    return my_dict
