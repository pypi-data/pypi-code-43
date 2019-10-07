from typing import Dict
from PyVoice.MyDict import MyDict, DictProperty


class EventInput(MyDict):
    """
    {
      "name": string,
      "parameters": {
        object
      },
      "languageCode": string
    }
    """

    name: str = DictProperty('name', str)
    parameters: Dict = DictProperty('parameters', dict)
    language_code: str = DictProperty('languageCode', str)

    def build(self, name: str, language_code: str, **parameters):
        self.name = name
        self.language_code = language_code
        self.parameters = parameters
        return self

    def add_parameters(self, **kwargs) -> dict:
        self.parameters.update(kwargs)
        return self.parameters
