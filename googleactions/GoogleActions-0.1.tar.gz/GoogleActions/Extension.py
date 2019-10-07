from PyVoice.MyDict import MyDict, DictProperty


class Extension(MyDict):
    """
    {
        "@type": string,
        field1: ...,
        ...
    }
    """
    type: str = DictProperty('@type', str)

    def build(self, type: str, **fields):

        if type is not None:
            self.type = type

        for key, value in fields.items():
            self[key] = value

        return self

    def add_fields(self, **kwargs) -> dict:

        for key, value in kwargs.items():
            self[key] = value

        return self
