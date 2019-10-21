def get_class(name):
    if not name:
        return None

    simple_name = name.rfind(".")
    classname = name[simple_name + 1:len(name)]
    module = __import__(name[0:simple_name], globals(), locals(), [classname])

    return getattr(module, classname)
