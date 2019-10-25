import jpype


class JavaPyConrad():
    """
    Helper class for invoking Python from CONRAD (on the Java side)
    """

    def __init__(self):
        self.globals_dict = dict()

    def eval(self, object, code, args):
        if object.autoConvertConradGrids:
            args = [(i.as_numpy() if jpype.JClass('edu.stanford.rsl.conrad.data.numeric.NumericGrid') else i)
                    for i in args]
        if object not in self.globals_dict:
            self.globals_dict[object] = dict()
        locals().update({**self.globals_dict[object]})
        rtn = eval(code)
        if object.autoConvertConradGrids:
            rtn = jpype.JClass('edu.stanford.rsl.conrad.data.numeric.NumericGrid').from_numpy(
                rtn) if hasattr(rtn, "__array__") else rtn
        self.globals_dict[object].update(locals())
        return rtn

    def exec(self, object, code, args):
        if object.autoConvertConradGrids:
            args = [(i.as_numpy() if hasattr(object, "as_numpy") else i) for i in args]
        if object not in self.globals_dict:
            self.globals_dict[object] = dict()
        locals().update({**self.globals_dict[object]})
        exec(code)
        self.globals_dict[object].update(locals())
