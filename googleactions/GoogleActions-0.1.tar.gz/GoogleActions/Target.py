from PyVoice.MyDict import MyDict, DictProperty
from .Argument import Argument
from .Extension import Extension


class Target(MyDict):
    """
    {
      "userId": string,
      "intent": string,
      "argument": {
        object(Argument)
      },
    }
    """
    user_id: str = DictProperty('userId', str)
    intent: str = DictProperty('intent', str)
    argument: Argument = DictProperty('argument', Argument)

    def build(self, intent: str=None, argument:Argument=None, user_id:str=None):
        if intent is not None:
            self.intent = intent
        if argument is not None:
            self.argument = argument
        if user_id is not None:
            self.user_id = user_id

        return self

    def add_argument(self, name:str=None, raw_text:str=None, text_value: str=None, status:Status=None, int_value:str=None,
                     float_value:str=None, bool_value:bool=False, datetime_value:str=None, place_value: Location=None,
                     extension:Extension=None, **structure_values) -> Argument:
        self.argument = Argument().build(name=name, raw_text=raw_text,text_value=text_value,status=status,
                                         int_value=int_value, float_value=float_value, bool_value=bool_value,
                                         datetime_value=datetime_value, place_value=place_value, extension=extension,
                                         **structure_values)

        return self.argument
