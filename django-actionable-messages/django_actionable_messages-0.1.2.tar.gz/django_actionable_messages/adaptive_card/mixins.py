from django_actionable_messages.adaptive_card.utils import FallbackOption, BlockElementHeight, SpacingStyle
from django_actionable_messages.utils import CardElement, CardException


class BaseElementMixin(CardElement):
    def __init__(self, fallback=None, separator: bool = None, spacing: SpacingStyle = None, item_id: str = None,
                 is_visible: bool = None, requires: dict = None, **kwargs):
        if fallback is not None:
            self.set_fallback(fallback)
        if separator is not None:
            self.set_separator(separator)
        if spacing is not None:
            self.set_spacing(spacing)
        if item_id is not None:
            self.set_id(item_id)
        if is_visible is not None:
            self.set_is_visible(is_visible)
        if requires is not None:
            self.set_requires(requires)
        super().__init__()

    def set_fallback(self, fallback):
        if isinstance(fallback, FallbackOption):
            self._data["fallback"] = fallback.value
        elif isinstance(fallback, BaseElementMixin):
            self._data["fallback"] = fallback.as_data()
        else:
            raise CardException("Invalid fallback type")

    def set_separator(self, value=True):
        self._data["separator"] = value

    def set_spacing(self, spacing: SpacingStyle):
        self._data["spacing"] = spacing.value

    def set_id(self, item_id: str):
        self._data["id"] = item_id

    def set_is_visible(self, visible=True):
        self._data["isVisible"] = visible

    def set_requires(self, requires: dict):
        self._data["requires"] = requires


class ElementMixin(BaseElementMixin):
    def __init__(self, height: BlockElementHeight = None, **kwargs):
        if height is not None:
            self.set_height(height)
        super().__init__(**kwargs)

    def set_height(self, height: BlockElementHeight):
        self._data["height"] = height.value
