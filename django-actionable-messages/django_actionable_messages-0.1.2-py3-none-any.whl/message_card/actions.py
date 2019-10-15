from typing import List

from django_actionable_messages.message_card.elements import Header, ActionTarget
from django_actionable_messages.utils import CardElement, CardException


class OpenUri(CardElement):
    def __init__(self, name: str, targets: List[ActionTarget] = None):
        self._data = {
            "@type": "OpenUri",
            "name": name
        }
        if targets:
            self.add_targets(targets)
        super().__init__()

    def set_name(self, name: str):
        self._data["name"] = name

    def add_targets(self, targets: List[ActionTarget]):
        for target in targets:
            self.add_target(target)

    def add_target(self, target: ActionTarget):
        targets = self._data.setdefault("targets", [])
        self._check_target(target, targets)
        self._data["targets"].append(target.as_data())

    def _check_target(self, target: ActionTarget, targets: list):
        os_type = target.get_os()
        os_list = (x["os"] for x in targets)
        if os_type in os_list:
            raise CardException("Target already set for '{}'".format(os_type))


class HttpPOST(CardElement):
    def __init__(self, name: str, target: str, headers: List[Header] = None, body: str = None,
                 body_content_type: str = None):
        self._data = {
            "@type": "HttpPOST",
            "name": name,
            "target": target
        }
        if headers:
            self.add_headers(headers)
        if body is not None:
            self.set_body(body)
        if body_content_type is not None:
            self.set_body_content_type(body_content_type)
        super().__init__()

    def set_name(self, name: str):
        self._data["name"] = name

    def set_target(self, target: str):
        self._data["target"] = target

    def add_header(self, header: Header):
        self._data.setdefault("headers", [])
        self._data["headers"].append(header.as_data())

    def add_headers(self, headers: List[Header]):
        self._data.setdefault("headers", [])
        self._data["headers"].extend(self._get_items_list(headers))

    def set_body(self, body: str):
        self._data["body"] = body

    def set_body_content_type(self, content_type: str):
        self._data["bodyContentType"] = content_type


class InvokeAddInCommand(CardElement):
    def __init__(self, name: str, add_in_id: str, desktop_command_id: str, initialization_context: dict = None):
        self._data = {
            "@type": "InvokeAddInCommand",
            "name": name,
            "addInId": add_in_id,
            "desktopCommandId": desktop_command_id
        }
        if initialization_context:
            self.set_initialization_context(initialization_context)
        super().__init__()

    def set_name(self, name: str):
        self._data["name"] = name

    def set_add_in_id(self, add_in_id: str):
        self._data["addInId"] = add_in_id

    def set_desktop_command_id(self, cmd_it: str):
        self._data["desktopCommandId"] = cmd_it

    def set_initialization_context(self, context: dict):
        self._data["initializationContext"] = context


class ActionCard(CardElement):
    def __init__(self, name: str, inputs: list = None, actions: list = None):
        self._data = {
            "@type": "ActionCard",
            "name": name
        }
        if inputs:
            self.add_inputs(inputs)
        if actions:
            self.add_actions(actions)
        super().__init__()

    def set_name(self, name: str):
        self._data["name"] = name

    def add_inputs(self, action_inputs: list):
        self._data.setdefault("inputs", [])
        self._data["inputs"].extend(self._get_items_list(action_inputs))

    def add_input(self, action_input):
        self._data.setdefault("inputs", [])
        self._data["inputs"].append(action_input.as_data())

    def add_actions(self, actions: list):
        self._data.setdefault("actions", [])
        self._data["actions"].extend(self._get_items_list(actions))

    def add_action(self, action):
        self._data.setdefault("actions", [])
        self._data["actions"].append(action.as_data())
