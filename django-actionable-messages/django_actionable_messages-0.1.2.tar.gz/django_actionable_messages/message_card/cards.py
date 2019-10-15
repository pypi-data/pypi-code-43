import uuid
from typing import List

from django_actionable_messages.utils import MESSAGE_CARD, Card


class MessageCard(Card):
    card_type = MESSAGE_CARD

    def __init__(self, title: str = None, text: str = None, originator: str = None, summary: str = None,
                 theme_color: str = None, correlation_id: str = None, auto_correlation_id=True,
                 expected_actors: List[str] = None, hide_original_body: bool = None, sections: list = None,
                 actions: list = None):
        self._payload = {
            "@type": "MessageCard",
            "@context": "https://schema.org/extensions"
        }

        if title is not None:
            self.set_title(title)
        if text is not None:
            self.set_text(text)
        if originator is not None:
            self.set_originator(originator)
        if summary is not None:
            self.set_summary(summary)
        if theme_color is not None:
            self.set_theme_color(theme_color)
        if correlation_id is not None or auto_correlation_id:
            self._payload["correlationId"] = correlation_id or str(uuid.uuid4())
        if expected_actors:
            self.set_expected_actors(expected_actors)
        if hide_original_body is not None:
            self.set_hide_original_body(hide_original_body)
        if sections:
            self.add_sections(sections)
        if actions:
            self.add_actions(actions)
        super().__init__()

    def set_title(self, title: str):
        self._payload["title"] = title

    def set_text(self, text: str):
        self._payload["text"] = text

    def set_originator(self, originator: str):
        self._payload["originator"] = originator

    def set_summary(self, summary: str):
        self._payload["summary"] = summary

    def set_theme_color(self, theme_color: str):
        self._payload["themeColor"] = theme_color

    def set_correlation_id(self, correlation_id: str):
        self._payload["correlationId"] = correlation_id

    def set_expected_actors(self, expected_actors: List[str]):
        self._payload["expectedActors"] = expected_actors

    def set_hide_original_body(self, hide_original_body=True):
        self._payload["hideOriginalBody"] = hide_original_body

    def add_sections(self, sections: list):
        self._payload.setdefault("sections", [])
        self._payload["sections"].extend(self._get_items_list(sections))

    def add_section(self, section):
        self._payload.setdefault("sections", [])
        self._payload["sections"].append(section.as_data())

    def add_actions(self, actions: list):
        self._payload.setdefault("potentialAction", [])
        self._payload["potentialAction"].extend(self._get_items_list(actions))

    def add_action(self, action):
        self._payload.setdefault("potentialAction", [])
        self._payload["potentialAction"].append(action.as_data())
