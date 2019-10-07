from typing import List, Optional
from PyVoice.MyDict import MyDict, DictProperty
from .Button import Button
from .OpenUriAction import OpenUriAction


class Card(MyDict):
    """
    {
      "title": string,
      "subtitle": string,
      "imageUri": string,
      "buttons": [
        {
          object(Button)
        }
      ],
    }
    """
    title: str = DictProperty('title', str)
    subtitle: str = DictProperty('subtitle', str)
    image_uri: str = DictProperty('imageUri', str)
    buttons_list: List[Button] = DictProperty('buttons', list)

    def build(self, title: str = None, image_uri: str = None, subtitle: str = None, *buttons: Button):

        self.buttons_list = []
        for item in buttons:
            assert isinstance(item, Button)
            self.buttons_list.append(item)

        if title is not None:
            self.title = title

        if image_uri is not None:
            self.image_uri = image_uri

        if subtitle is not None:
            self.subtitle = subtitle

        return self

    def add_button(self, title: str, uri: str) -> Button:
        button = Button().build(title=title, open_uri_action=OpenUriAction().build(uri=uri))
        self.buttons_list.append(button)

        return button
