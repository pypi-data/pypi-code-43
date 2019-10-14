class Param(object):
    CommandCode = -1
    
    def __init__(self):
        raise NotImplementedError
    
    def validate(self):
        return True
    
    @classmethod
    def load_from_cmd(cls, cmd):
        if cls.CommandCode < 0 or not isinstance(cls.CommandCode, int):
            raise Exception("Invalid CommandCode = {}, CommandCode should be not less than 0, and should be integer".format(cls.CommandCode))
        if cmd.code != cls.CommandCode:
            raise Exception("Invalid code to do this, code = {}".format(cmd.code))
        param = cls()
        keys = param.__dict__.keys()
        for key in keys:
            setattr(param, key, cmd.params.get(key))
        status = param.validate()
        if not status:
            raise Exception("Invalid params.")
        return param