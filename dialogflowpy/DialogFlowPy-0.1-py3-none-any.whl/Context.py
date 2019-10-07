from PyVoice.MyDict import MyDict, DictProperty


class Context(MyDict):
    """
    {
      "name": string,
      "lifespanCount": number,
      "parameters": {
        object
      }
    }
    """

    name: str = DictProperty('name', str)
    lifespan_count: int = DictProperty('lifespanCount', int)
    parameters: dict = DictProperty('parameters', dict)

    def build(self, name: str, lifespan_count: int, **parameters):
        self.name = name
        self.lifespan_count = lifespan_count
        self.parameters = parameters
        return self

    def add_parameters(self, **parameters) -> dict:
        self.parameters.update(**parameters)
        return self.parameters

    def update_parameters(self, **parameters) -> dict:
        self.parameters.update(**parameters)
        return self.parameters
