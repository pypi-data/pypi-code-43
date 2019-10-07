from .Button import Button
from . import ActionType
from .OpenUrlAction import OpenUrlAction
from PyVoice.MyDict import MyDict, DictProperty


class Action(MyDict):
    """
    {
      "type": enum(ActionType),
      "button": {
        object(Button)
      },
    }
    type
    enum(ActionType)
    Type of action.

    button
    object(Button)
    Button label and link.
    """

    type: ActionType = DictProperty('type', ActionType)
    button: Button = DictProperty('button', Button)

    def build(self, button: Button=None, action_type: ActionType=None):

        if button is not None:
            self.button = button

        if action_type is not None:
            self.action_type = action_type

        return self

    def add_button(self, title: str, url:str) -> Button:
        assert isinstance(title, str)
        assert isinstance(url, str)

        self.button = Button().build(title=title, open_url_action=OpenUrlAction().build(url=url))

        return self.button
