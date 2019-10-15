from typing import List

from django_actionable_messages.message_card.elements import Fact, HeroImage
from django_actionable_messages.utils import CardElement


class Section(CardElement):
    def __init__(self, start_group: bool = False, title: str = None, text: str = None, activity_image: str = None,
                 activity_title: str = None, activity_subtitle: str = None, activity_text: str = None,
                 hero_image: HeroImage = None, facts: List[Fact] = None, actions: list = None):
        self._data = {}
        if start_group:
            self.set_start_group(start_group)
        if title is not None:
            self.set_title(title)
        if text is not None:
            self.set_text(text)
        if activity_image is not None:
            self.set_activity_image(activity_image)
        if activity_title is not None:
            self.set_activity_title(activity_title)
        if activity_subtitle is not None:
            self.set_activity_subtitle(activity_subtitle)
        if activity_text is not None:
            self.set_activity_text(activity_text)
        if hero_image is not None:
            self.set_hero_image(hero_image)
        if facts:
            self.add_facts(facts)
        if actions:
            self.add_potential_actions(actions)
        super().__init__()

    def set_start_group(self, start_group=True):
        self._data["startGroup"] = start_group

    def set_title(self, title: str):
        self._data["title"] = title

    def set_text(self, text: str):
        self._data["text"] = text

    def set_activity(self, image: str = None, title: str = None, subtitle: str = None, text: str = None):
        if image is not None:
            self.set_activity_image(image)
        if title is not None:
            self.set_activity_title(title)
        if subtitle is not None:
            self.set_activity_subtitle(subtitle)
        if text is not None:
            self.set_activity_text(text)

    def set_activity_image(self, image: str):
        self._data["activityImage"] = image

    def set_activity_title(self, title: str):
        self._data["activityTitle"] = title

    def set_activity_subtitle(self, subtitle: str):
        self._data["activitySubtitle"] = subtitle

    def set_activity_text(self, text: str):
        self._data["activityText"] = text

    def set_hero_image(self, hero_image: HeroImage):
        self._data["heroImage"] = hero_image.as_data()

    def add_facts(self, facts: List[Fact]):
        self._data.setdefault("facts", [])
        self._data["facts"].extend(self._get_items_list(facts))

    def add_fact(self, fact: Fact):
        self._data.setdefault("facts", [])
        self._data["facts"].append(fact.as_data())

    def add_potential_actions(self, actions: list):
        self._data.setdefault("potentialAction", [])
        self._data["potentialAction"].extend(self._get_items_list(actions))

    def add_potential_action(self, potential_action):
        self._data.setdefault("potentialAction", [])
        self._data["potentialAction"].append(potential_action.as_data())
