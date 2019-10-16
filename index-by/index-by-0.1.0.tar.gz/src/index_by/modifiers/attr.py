class AttributeModifier:

    def __init__(self, attr_name):
        self._attr_name = attr_name

    def __call__(self, obj):
        return getattr(obj, self._attr_name)


class AttributesModifier:

    def __init__(self, attr_names):
        self._attr_names = attr_names

    def __call__(self, obj):
        return tuple(getattr(obj, attr_name) for attr_name in self._attr_names)
