from typing import List
from .RichResponse import RichResponse
from .SimpleResponse import SimpleResponse
from PyVoice.MyDict import MyDict, DictProperty


class InputPrompt(MyDict):
    """
    Input Prompt

    class for Google
    {
      "richInitialPrompt": {
        object(RichResponse)
      },
      "noInputPrompts": [
        {
          object(SimpleResponse)
        }
      ],
    }
    """
    rich_initial_prompt: RichResponse = DictProperty('richInitialPrompt', RichResponse)
    no_input_prompts: List[SimpleResponse]= DictProperty('noInputPrompts', list)

    def build(self, rich_initial_prompt: RichResponse=None, *no_input_prompts:SimpleResponse):
        self.rich_initial_prompt = rich_initial_prompt
        for item in no_input_prompts:
            self.no_input_prompts.append(item)
        return self

    def add_rich_initial_prompt(self) -> RichResponse:
        self.rich_initial_prompt = RichResponse()
        return self.rich_initial_prompt

    def add_no_input_prompts(self, *no_input_prompts: SimpleResponse) -> List[SimpleResponse]:
        for item in no_input_prompts:
            assert isinstance(item, SimpleResponse)
            self.no_input_prompts.append(item)

        return self.no_input_prompts

    def add_no_input_prompt(self, text_to_speech:str=None, ssml:str=None, display_text:str =None) -> SimpleResponse:
        no_input_prompt = SimpleResponse().build(text_to_speech=text_to_speech, ssml=ssml, display_text=display_text)
        self.no_input_prompts.append(no_input_prompt)

        return no_input_prompt
