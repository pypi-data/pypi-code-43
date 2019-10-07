from typing import List
from PyVoice.MyDict import MyDict, DictProperty
from .InputPrompt import InputPrompt
from .ExpectedIntent import ExpectedIntent
from .RichResponse import RichResponse


class ExpectedInput(MyDict):
    """
    {
      "inputPrompt": {
        object(InputPrompt)
      },
      "possibleIntents": [
        {
          object(ExpectedIntent)
        }
      ],
      "speechBiasingHints": [
        string
      ],
    }
    """
    
    input_prompt: InputPrompt = DictProperty('inputPrompt', InputPrompt)
    possible_intents: List[ExpectedIntent] = DictProperty('possibleIntents', list)
    speech_biasing_hints: List[str] = DictProperty('speechBiasingHints', list)

    def build(self, speech_biasing_hints_list: List[str]=None, input_prompt: InputPrompt=None,
              possible_intents_list: List[ExpectedIntent]=None):
        self.speech_biasing_hints = speech_biasing_hints_list
        self.input_prompt = input_prompt
        self.possible_intents = possible_intents_list

        return self

    def add_speech_biasing_hint(self, *speech_biasing_hints:str) -> List[str]:
        for item in speech_biasing_hints:
            assert isinstance(item, str)
            self.speech_biasing_hints.append(item)

        return self.speech_biasing_hints

    def add_possible_intent(self, *possible_intents: ExpectedIntent) -> List[ExpectedIntent]:
        for item in possible_intents:
            assert isinstance(item, ExpectedIntent)
            self.possible_intents.append(item)

        return self.possible_intents

    def add_input_prompt(self, rich_initial_prompt: RichResponse=None, *no_input_prompts:InputPrompt) -> InputPrompt:
        self.input_prompt = InputPrompt().build(rich_initial_prompt=rich_initial_prompt,
                                               *no_input_prompts)
        return self.input_prompt
