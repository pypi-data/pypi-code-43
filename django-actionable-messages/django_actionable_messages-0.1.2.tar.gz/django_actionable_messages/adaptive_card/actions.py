from typing import Union

from django_actionable_messages.adaptive_card.utils import FallbackOption, ActionStyle
from django_actionable_messages.utils import CardElement, CardException


class ActionMixin(CardElement):
    def __init__(self, title: str = None, icon_url: str = None, style: ActionStyle = None, fallback=None,
                 requires: dict = None, **kwargs):
        if title is not None:
            self.set_title(title)
        if icon_url is not None:
            self.set_icon_url(icon_url)
        if style is not None:
            self.set_style(style)
        if fallback is not None:
            self.set_fallback(fallback)
        if requires is not None:
            self.set_requires(requires)
        super().__init__()

    def set_title(self, title: str):
        self._data["title"] = title

    def set_icon_url(self, url: str):
        self._data["iconUrl"] = url

    def set_style(self, style: ActionStyle):
        self._data["style"] = style.value

    def set_fallback(self, fallback):
        if isinstance(fallback, FallbackOption):
            self._data["fallback"] = fallback.value
        elif isinstance(fallback, ActionMixin):
            self._data["fallback"] = fallback.as_data()
        else:
            raise CardException("Invalid fallback type")

    def set_requires(self, requires: dict):
        self._data["requires"] = requires


class OpenUrl(ActionMixin):
    def __init__(self, url: str, **kwargs):
        self._data = {
            "type": "Action.OpenUrl",
            "url": url
        }
        super().__init__(**kwargs)

    def set_url(self, url: str):
        self._data["url"] = url


class Submit(ActionMixin):
    def __init__(self, data: Union[str, dict] = None, **kwargs):
        self._data = {
            "type": "Action.Submit"
        }
        if data is not None:
            self.set_data(data)
        super().__init__(**kwargs)

    def set_data(self, data: Union[str, dict]):
        self._data["data"] = data


class ShowCard(ActionMixin):
    def __init__(self, card=None, **kwargs):
        self._data = {
            "type": "Action.ShowCard"
        }
        if card is not None:
            self.set_card(card)
        super().__init__(**kwargs)

    def set_card(self, card):
        self._data["card"] = card.payload


class TargetElement(CardElement):
    def __init__(self, element_id: str, is_visible: bool = None):
        self._data = {
            "elementId": element_id
        }
        if is_visible is not None:
            self.set_is_visible(is_visible)
        super().__init__()

    def set_element_id(self, element_id: str):
        self._data["elementId"] = element_id

    def set_is_visible(self, value=True):
        self._data["isVisible"] = value


class ToggleVisibility(ActionMixin):
    def __init__(self, target_elements: list = None, **kwargs):
        self._data = {
            "type": "Action.ToggleVisibility"
        }
        if target_elements:
            self.set_target_elements(target_elements)
        super().__init__(**kwargs)

    def set_target_elements(self, elements: list):
        self._data["targetElements"] = []
        for element in elements:
            if isinstance(element, TargetElement):
                self._data["targetElements"].append(element.as_data())
            elif isinstance(element, str):
                self._data["targetElements"].append(element)
            else:
                raise CardException("Invalid target element type")
