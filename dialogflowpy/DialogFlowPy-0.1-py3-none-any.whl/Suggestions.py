from typing import List
from PyVoice.MyDict import MyDict, DictProperty
from .Suggestion import Suggestion


class Suggestions(MyDict):
    """
    {
      "suggestions": [
        {
          object(Suggestion)
        }
      ]
    }
    """

    suggestions: List[Suggestion] = DictProperty('suggestions', list)

    def build(self, *suggestions: List[Suggestion]):
        self.suggestions = []
        for item in suggestions:
            self.suggestions.append(item)
        return self

    def add_suggestions(self, *suggestions: List[Suggestion]):
        for item in suggestions:
            self.suggestions.append(item)
        return self
