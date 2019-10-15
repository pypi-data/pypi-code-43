from typing import List

from django_actionable_messages.message_card.elements import InputChoice
from django_actionable_messages.message_card.utils import ChoiceStyle
from django_actionable_messages.utils import CardElement, CardException


class InputMixin(CardElement):
    input_type = None

    def __init__(self, input_id: str = None, title: str = None, value: str = None, is_required: bool = None, **kwargs):
        self._data = {
            "@type": self.input_type
        }
        if input_id is not None:
            self.set_id(input_id)
        if title is not None:
            self.set_title(title)
        if value is not None:
            self.set_value(value)
        if is_required is not None:
            self.set_is_required(is_required)
        super().__init__()

    def set_id(self, input_id: str):
        self._data["id"] = input_id

    def set_title(self, title: str):
        self._data["title"] = title

    def set_value(self, value: str):
        self._data["value"] = value

    def set_is_required(self, is_required=True):
        self._data["isRequired"] = is_required


class TextInput(InputMixin):
    input_type = "TextInput"

    def __init__(self, max_length: int = None, is_multiline: bool = False, **kwargs):
        super().__init__(**kwargs)
        if max_length is not None:
            self.set_max_length(max_length)
        self.set_is_multiline(is_multiline)

    def set_max_length(self, max_length: int):
        self._data["maxLength"] = max_length

    def set_is_multiline(self, is_multiline=True):
        self._data["isMultiline"] = is_multiline


class DateInput(InputMixin):
    input_type = "DateInput"

    def __init__(self, include_time: bool = None, **kwargs):
        super().__init__(**kwargs)
        if include_time is not None:
            self.set_include_time(include_time)

    def set_include_time(self, include_time=True):
        self._data["includeTime"] = include_time


class MultiChoiceInput(InputMixin):
    input_type = "MultichoiceInput"

    def __init__(self, choices: List[InputChoice] = None, is_multi_select: bool = None, style: ChoiceStyle = None,
                 **kwargs):
        super().__init__(**kwargs)
        if choices:
            self.add_choices(choices)
        if is_multi_select is not None:
            self.set_is_multi_select(is_multi_select)
        if style is not None:
            self.set_style(style)

    def add_choices(self, choices: List[InputChoice]):
        for choice in choices:
            self.add_choice(choice)

    def add_choice(self, choice: InputChoice):
        choices = self._data.setdefault("choices", [])
        self._check_choice(choice, choices)
        self._data["choices"].append(choice.as_data())

    def set_is_multi_select(self, is_multi_select=True):
        self._data["isMultiSelect"] = is_multi_select

    def set_style(self, style: ChoiceStyle):
        self._data["style"] = style.value

    def _check_choice(self, choice, choices):
        choice_value = choice.get_value()
        values_list = (c["value"] for c in choices)
        if choice_value in values_list:
            raise CardException("Choice with this 'value' [{}] already added".format(choice_value))
