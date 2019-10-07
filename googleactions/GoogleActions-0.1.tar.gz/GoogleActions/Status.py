from PyVoice.MyDict import MyDict, DictProperty


class Status(MyDict):
    """
    {
      "code": number,
      "message": string,
      "details": [
        {
          "@type": string,
          field1: ...,
          ...
        }
      ]
    }
    """

    code: int = DictProperty('code', int)
    message: str = DictProperty('message', str)
    type: str = DictProperty('@type', str)

    def build(self, code: int=None, message:str=None, type: str=None, **fields):
        if code is not None:
            self.code = code

        if message is not None:
            self.message = message

        if type is not None:
            self.type = type

        for key, value in fields.items():
            self[key] = value

        return self

    def add_fields(self, **fields) -> dict:

        for key, value in fields.items():
            self[key] = value

        return self
