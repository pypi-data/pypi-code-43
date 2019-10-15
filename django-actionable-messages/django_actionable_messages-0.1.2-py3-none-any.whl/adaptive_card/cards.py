from typing import Union

from django_actionable_messages.adaptive_card.elements import Image
from django_actionable_messages.adaptive_card.utils import VERSIONS, Style, VerticalAlignment
from django_actionable_messages.utils import ADAPTIVE_CARD, Card, CardException


class AdaptiveCard(Card):
    card_type = ADAPTIVE_CARD

    def __init__(self, version: str = None, schema: str = None, inputs: list = None, actions: list = None,
                 select_action=None, style: Style = None, hide_original_body: bool = None, fallback_text: str = None,
                 background_image: Union[str, Image] = None, min_height: str = None, speak: str = None,
                 lang: str = None, vertical_content_alignment: VerticalAlignment = None):
        self._payload = {
            "type": "AdaptiveCard"
        }
        if version is not None:
            self.set_version(version)
        if schema is not None:
            self.set_schema(schema)
        if inputs:
            self.add_elements(inputs)
        if actions:
            self.add_actions(actions)
        if select_action is not None:
            self.set_select_action(select_action)
        if style is not None:
            self.set_style(style)
        if hide_original_body is not None:
            self.set_hide_original_body(hide_original_body)
        if fallback_text is not None:
            self.set_fallback_text(fallback_text)
        if background_image is not None:
            self.set_background_image(background_image)
        if min_height is not None:
            self.set_min_height(min_height)
        if speak is not None:
            self.set_speak(speak)
        if lang is not None:
            self.set_lang(lang)
        if vertical_content_alignment is not None:
            self.set_vertical_content_alignment(vertical_content_alignment)
        super().__init__()

    def set_version(self, version: str):
        if version not in VERSIONS:
            raise CardException("Invalid version. Supported versions are: {}".format(VERSIONS))
        self._payload["version"] = version

    def set_schema(self, schema: str):
        self._payload["$schema"] = schema

    def set_select_action(self, action):
        self._payload["selectAction"] = action.as_data()

    def set_style(self, style: Style):
        self._payload["style"] = style.value

    def set_hide_original_body(self, value=True):
        self._payload["hideOriginalBody"] = value

    def set_fallback_text(self, text: str):
        self._payload["fallbackText"] = text

    def set_background_image(self, image: Union[str, Image]):
        if isinstance(image, Image):
            self._payload["backgroundImage"] = image.as_data()
        elif isinstance(image, str):
            self._payload["backgroundImage"] = image
        else:
            raise CardException("Invalid image type")

    def set_min_height(self, height: str):
        self._payload["minHeight"] = height

    def set_speak(self, text: str):
        self._payload["speak"] = text

    def set_lang(self, lang: str):
        self._payload["lang"] = lang

    def set_vertical_content_alignment(self, alignment: VerticalAlignment):
        self._payload["verticalContentAlignment"] = alignment.value

    def add_element(self, element):
        self._payload.setdefault("body", [])
        self._payload["body"].append(element.as_data())

    def add_elements(self, elements: list):
        self._payload.setdefault("body", [])
        self._payload["body"].extend(self._get_items_list(elements))

    def add_action(self, action):
        self._payload.setdefault("actions", [])
        self._payload["actions"].append(action.as_data())

    def add_actions(self, actions: list):
        self._payload.setdefault("actions", [])
        self._payload["actions"].extend(self._get_items_list(actions))
