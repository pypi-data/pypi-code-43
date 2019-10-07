from typing import List
from PyVoice.MyDict import MyDict, DictProperty
from .Image import Image
from .Button import Button
from .ColumnProperties import ColumnProperties
from .Row import Row
from .Cell import Cell
from .OpenUrlAction import OpenUrlAction
from . import HorizontalAlignment


class TableCard(MyDict):
    """
    {
      "title": string,
      "subtitle": string,
      "image": {
        object(Image)
      },
      "columnProperties": [
        {
          object(ColumnProperties)
        }
      ],
      "rows": [
        {
          object(Row)
        }
      ],
      "buttons": [
        {
          object(Button)
        }
      ]
    }
    """

    title: str = DictProperty('title', str)
    subtitle: str = DictProperty('subtitle', str)
    image: Image = DictProperty('image', Image)
    column_properties: List[ColumnProperties] = DictProperty('columnProperties', list)
    rows: List[Row] = DictProperty('rows', list)
    buttons: List[Button] = DictProperty('buttons', list)

    def build(self, title: str, subtitle: str, image: Image, column_properties: List[ColumnProperties],
              rows: List[Row], buttons: List[Button]):
        self.title = title
        self.subtitle = subtitle
        self.image = image
        self.column_properties = column_properties
        self.rows = rows
        self.buttons = buttons

        return self

    def add_image(self, url: str, accessibility_text: str = None, height: int = 0, width: int = 0) -> Image:
        self.image = Image().build(url=url, accessibility_text=accessibility_text, height=height, width=width)
        return self.image

    def add_column_properties(self, *column_properties: ColumnProperties) -> List[ColumnProperties]:
        for item in column_properties:
            assert isinstance(item, ColumnProperties)
            self.column_properties.append(item)
        return self.column_properties

    def add_column_property(self, header: str, horizontal_alignment: HorizontalAlignment) -> ColumnProperties:
        column_property = ColumnProperties().build(header=header, horizontal_alignment=horizontal_alignment)
        return column_property

    def add_rows(self, *rows:Row) -> List[Row]:
        for item in rows:
            assert isinstance(item, Row)
            self.rows.append(item)
        return self.rows

    def add_row(self, divider_after:bool=False, *cells:Cell) -> Row:
        row = Row().build(divider_after=divider_after, *cells)
        return row

    def add_buttons(self, *buttons) -> List[Button]:
        for item in buttons:
            assert isinstance(item, Button)
            self.buttons.append(item)

        return self.buttons

    def add_button(self, title: str, url:str) -> Button:
        assert isinstance(title, str)
        assert isinstance(url, str)

        self.button = Button().build(title=title, open_url_action=OpenUrlAction().build(url=url))

        return self.button