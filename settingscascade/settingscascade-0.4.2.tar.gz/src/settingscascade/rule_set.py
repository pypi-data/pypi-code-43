from settingscascade.selector import Selector


class RuleSet:
    def __init__(self, selector: str, order: int, **kwargs):
        self.selector: Selector = Selector(selector)
        self.order = order
        self.__keys__ = kwargs.keys()
        for key, val in kwargs.items():
            setattr(self, key, val)

    def __repr__(self):
        vals = ", ".join(f"{key}={getattr(self, key)}" for key in self.__keys__)
        return f"{self.selector.text}: {vals}"
