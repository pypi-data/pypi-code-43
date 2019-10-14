from .errors import ValidateParamsFailedError

class Param(object):
    
    def __init__(self):
        raise NotImplementedError
    
    def validate(self):
        return True
    
    @classmethod
    def load_from_cmd(cls, cmd):
        param = cls()
        keys = param.__dict__.keys()
        for key in keys:
            setattr(param, key, cmd.params.get(key))
        status = param.validate()
        if not status:
            raise ValidateParamsFailedError("Invalid params.")
        return param
