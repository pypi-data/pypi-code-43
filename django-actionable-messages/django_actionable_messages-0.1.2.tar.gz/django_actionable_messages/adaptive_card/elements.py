from typing import Union, List

from django_actionable_messages.adaptive_card.mixins import BaseElementMixin, ElementMixin
from django_actionable_messages.adaptive_card.utils import (
    HorizontalAlignment, Color, FontType, FontSize, FontWeight, BlockElementHeight, ImageSize, ImageStyle
)
from django_actionable_messages.utils import CardElement, CardException


class TextBlock(ElementMixin):
    def __init__(self, text: str, color: Color = None, font_type: FontType = None,
                 horizontal_alignment: HorizontalAlignment = None, is_subtle: bool = None, max_lines: int = None,
                 size: FontSize = None, weight: FontWeight = None, wrap: bool = None, **kwargs):
        self._data = {
            "type": "TextBlock",
            "text": text
        }
        if color is not None:
            self.set_color(color)
        if font_type is not None:
            self.set_font_type(font_type)
        if horizontal_alignment is not None:
            self.set_horizontal_alignment(horizontal_alignment)
        if is_subtle is not None:
            self.set_is_subtle(is_subtle)
        if max_lines is not None:
            self.set_max_lines(max_lines)
        if size is not None:
            self.set_size(size)
        if weight is not None:
            self.set_weight(weight)
        if wrap is not None:
            self.set_wrap(wrap)
        super().__init__(**kwargs)

    def set_text(self, text: str):
        self._data["text"] = text

    def set_color(self, color: Color):
        self._data["color"] = color.value

    def set_font_type(self, font_type: FontType):
        self._data["fontType"] = font_type.value

    def set_horizontal_alignment(self, alignment: HorizontalAlignment):
        self._data["horizontalAlignment"] = alignment.value

    def set_is_subtle(self, value=True):
        self._data["isSubtle"] = value

    def set_max_lines(self, max_lines: int):
        self._data["maxLines"] = max_lines

    def set_size(self, size: FontSize):
        self._data["size"] = size.value

    def set_weight(self, weight: FontWeight):
        self._data["weight"] = weight.value

    def set_wrap(self, value=True):
        self._data["wrap"] = value


class Image(BaseElementMixin):
    def __init__(self, url: str, alternate_text: str = None, background_color: str = None,
                 height: Union[str, BlockElementHeight] = None, horizontal_alignment: HorizontalAlignment = None,
                 select_action=None, size: ImageSize = None, style: ImageStyle = None, width: str = None, **kwargs):
        self._data = {
            "type": "Image",
            "url": url
        }
        if alternate_text is not None:
            self.set_alternate_text(alternate_text)
        if background_color is not None:
            self.set_background_color(background_color)
        if height is not None:
            self.set_height(height)
        if horizontal_alignment is not None:
            self.set_horizontal_alignment(horizontal_alignment)
        if select_action is not None:
            self.set_select_action(select_action)
        if size is not None:
            self.set_size(size)
        if style is not None:
            self.set_style(style)
        if width is not None:
            self.set_width(width)
        super().__init__(**kwargs)

    def set_url(self, url: str):
        self._data["url"] = url

    def set_alternate_text(self, text: str):
        self._data["altText"] = text

    def set_background_color(self, color: str):
        self._data["backgroundColor"] = color

    def set_height(self, height: Union[str, BlockElementHeight]):
        if isinstance(height, BlockElementHeight):
            self._data["height"] = height.value
        elif isinstance(height, str):
            self._data["height"] = height
        else:
            raise CardException("Invalid height type")

    def set_horizontal_alignment(self, alignment: HorizontalAlignment):
        self._data["horizontalAlignment"] = alignment.value

    def set_select_action(self, action):
        self._data["selectAction"] = action.as_data()

    def set_size(self, size: ImageSize):
        self._data["size"] = size.value

    def set_style(self, style: ImageStyle):
        self._data["style"] = style.value

    def set_width(self, width: str):
        self._data["width"] = width


class MediaSource(CardElement):
    def __init__(self, mime_type: str, url: str):
        self._data = {
            "mimeType": mime_type,
            "url": url
        }
        super().__init__()


class Media(ElementMixin):
    def __init__(self, sources: List[MediaSource], poster: str = None, alternate_text: str = None, **kwargs):
        self._data = {
            "type": "Media",
            "sources": self._get_items_list(sources)
        }
        if poster is not None:
            self.set_poster(poster)
        if alternate_text is not None:
            self.set_alternate_text(alternate_text)
        super().__init__(**kwargs)

    def add_sources(self, sources: List[MediaSource]):
        self._data["sources"].extend(self._get_items_list(sources))

    def add_source(self, source: MediaSource):
        self._data["sources"].append(source.as_data())

    def set_poster(self, poster: str):
        self._data["poster"] = poster

    def set_alternate_text(self, text: str):
        self._data["altText"] = text


class TextRun(CardElement):
    def __init__(self, text: str, color: Color = None, font_type: FontType = None, highlight: bool = None,
                 is_subtle: bool = None, italic: bool = None, select_action=None, size: FontSize = None,
                 strike_through: bool = None, weight: FontWeight = None):
        self._data = {
            "type": "TextRun",
            "text": text
        }
        if color is not None:
            self.set_color(color)
        if font_type is not None:
            self.set_font_type(font_type)
        if highlight is not None:
            self.set_highlight(highlight)
        if is_subtle is not None:
            self.set_is_subtle(is_subtle)
        if italic is not None:
            self.set_italic(italic)
        if select_action:
            self.set_select_action(select_action)
        if size is not None:
            self.set_size(size)
        if strike_through is not None:
            self.set_strike_through(strike_through)
        if weight is not None:
            self.set_weight(weight)
        super().__init__()

    def set_text(self, text: str):
        self._data["text"] = text

    def set_color(self, color: Color):
        self._data["color"] = color.value

    def set_font_type(self, font_type: FontType):
        self._data["fontType"] = font_type.value

    def set_highlight(self, value=True):
        self._data["highlight"] = value

    def set_is_subtle(self, value=True):
        self._data["isSubtle"] = value

    def set_italic(self, value=True):
        self._data["italic"] = value

    def set_select_action(self, action):
        self._data["selectAction"] = action.as_data()

    def set_size(self, size: FontSize):
        self._data["size"] = size.value

    def set_strike_through(self, value=True):
        self._data["strikethrough"] = value

    def set_weight(self, weight: FontWeight):
        self._data["weight"] = weight.value


class RichTextBlock(ElementMixin):
    def __init__(self, inlines: list, horizontal_alignment: HorizontalAlignment = None,
                 **kwargs):
        self._data = {
            "type": "RichTextBlock"
        }
        self.set_inlines(inlines)
        if horizontal_alignment is not None:
            self.set_horizontal_alignment(horizontal_alignment)
        super().__init__(**kwargs)

    def set_inlines(self, inlines: list):
        self._data["inlines"] = []
        for item in inlines:
            if isinstance(item, str):
                self._data["inlines"].append(item)
            elif isinstance(item, TextRun):
                self._data["inlines"].append(item.as_data())
            else:
                raise CardException("Invalid inline type")

    def set_horizontal_alignment(self, alignment: HorizontalAlignment):
        self._data["horizontalAlignment"] = alignment.value
