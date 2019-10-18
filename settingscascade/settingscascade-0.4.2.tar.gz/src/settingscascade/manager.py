from contextlib import contextmanager
from typing import Callable, Dict, List, Optional, Type

from jinja2 import Environment
from jinja2.meta import find_undeclared_variables

from settingscascade.element_schema import ElementSchema
from settingscascade.logger import logger
from settingscascade.rule_set import RuleSet
from settingscascade.selector import Item, Selector, SelectorStorage
from settingscascade.utils import ensure_list


class SettingsManager:
    """A Settingsmanager object.

    :param data: a list of settings dictionaries
    :param els: a List of ElemeentSchema objects, If not specified, no elements will be created
    """

    def __init__(
        self, data: List[dict], els: Optional[List[Type[ElementSchema]]] = None
    ):
        self.els = self._build_levels(els or [])
        self.store: SelectorStorage = SelectorStorage()
        self._contexts: List[str] = [""]
        self.load_data_objects(data)
        self.jinja_env: Environment = Environment()

    def load_data_objects(self, data_objects, map_key: str = "", selector: str = ""):
        if not isinstance(data_objects, (dict, list)):
            raise TypeError(
                f"Attempting to load a value into {map_key} instead of a map"
            )
        for data in ensure_list(data_objects):
            self.load_data(data, map_key, selector)

    @staticmethod
    def _build_levels(
        levels: List[Type[ElementSchema]]
    ) -> Dict[str, Type[ElementSchema]]:
        level_dict: Dict[str, Type[ElementSchema]] = {}
        for level in levels:
            if not issubclass(level, ElementSchema):
                raise TypeError("Levels must be strings or ElementSchema classes")
            level_dict[level._name_] = level  # pylint: disable=protected-access
        return level_dict

    def add_filter(self, name: str, func: Callable):
        self.jinja_env.filters[name] = func

    @property
    def current_context(self) -> str:
        """Gets a string that represents the current context used
        for settings lookups
        :return: str
        """
        return " ".join(ctx for ctx in self._contexts if ctx)

    def with_context(self, new_context):
        return ElementSchema(self)(ctx=new_context)

    def parent(self):
        parent = self.current_context.split(" ")[:-1]
        return ElementSchema(self)(ctx=" ".join(parent))

    @contextmanager
    def context(self, new_context: str = ""):
        """Add context onto the current context.
        This takes a string and appends it to the existing
        context. For example (using html elements-)

        .. code-block:: python

            with config.context("body h1.intro"):
                with config.context("div.myel"):
                    config.current_context == "body h1.intro div.myel"

        """
        self.push_context(new_context)
        yield
        self.pop_context()

    def push_context(self, new_context: str = ""):
        self._contexts.append(new_context)

    def pop_context(self):
        self._contexts.pop()

    def clear_context(self):
        self._contexts = [""]

    @staticmethod
    def class_from_map(data):
        klass = data.pop("_name_", None)
        return f".{klass}" if klass else ""

    @staticmethod
    def id_from_map(data):
        identifier = data.pop("_id_", None)
        return f"#{identifier}" if identifier else ""

    def load_data(self, data: dict, next_item: str = "", selector: str = ""):
        """Loads a settings dictionary into the rule stack.

        :param data: A settings dictionary. Keys should either be selectors or value names.
        :param next_item: The key for this rule-set. Pulled from the parent dict when loading
            recursively.
        :param selector: The full context selector for any parent rule-sets that should be
            added to the selector for this one
        """
        next_item = "".join(
            (next_item, self.class_from_map(data), self.id_from_map(data))
        )
        selector = " ".join((selector, next_item)).strip()
        settings = {}
        for key, val in data.items():
            if key in self.els or Item(key).score > (0, 0, 1):
                self.load_data_objects(val, key, selector)
            else:
                if next_item:
                    el = Item(next_item).el
                    if el:
                        schema = self.els[el]
                        schema.check_type(key, val)
                settings[key] = val
        self.store.add(RuleSet(selector, order=len(self.store), **settings))

    def get_value(self, selector: str, key: str):
        if key == "config":
            return self
        val = self.lookup_value(selector, key)
        # Only strings will get passed to the jinja templater
        return self.resolve_string(val, selector)

    def resolve_string(self, val, selector):
        if isinstance(val, list):
            return [self.resolve_string(item, selector) for item in val]
        if not isinstance(val, str):
            return val
        return self.render_value(selector, val)

    def __getattr__(self, item):
        if item in self.els:
            return self.els[item](self)
        return self.get_value(self.current_context, item)

    def render_value(self, selector, val):
        missing_keys = find_undeclared_variables(self.jinja_env.parse(val))
        template_context = {key: self.get_value(selector, key) for key in missing_keys}
        return self.jinja_env.from_string(val).render(**template_context)

    def lookup_value(self, selector: str, key: str):
        if key == "name":
            return Selector(selector).items[-1].klass
        if key == "id":
            return Selector(selector).items[-1].identifier
        for rule in self.store.lookup_rules(selector):
            if hasattr(rule, key):
                return getattr(rule, key)
        logger.debug("No selector found- selectors:")
        for ruleset in self.store:
            logger.debug(f"{ruleset.selector}- keys: {list(ruleset.__keys__)}")
        raise ValueError(f"Could not find value: {key} using selector: {selector}.")

    def return_value_stack(self, selector: str):
        for rule in self.store.lookup_rules(selector):
            yield rule
