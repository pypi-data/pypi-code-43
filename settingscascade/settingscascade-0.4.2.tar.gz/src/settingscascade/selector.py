import re
from collections import Counter, namedtuple
from functools import reduce
from operator import add
from typing import Iterable, Optional, Set, Tuple, Union

from sortedcontainers import SortedKeyList


class Score(namedtuple("Score", ["ids", "classes", "els"])):
    def __add__(self, other):
        if not isinstance(other, Score):
            raise NotImplementedError()
        return Score(*(a + b for a, b in zip(self, other)))

    def __eq__(self, other):
        return all(self[i] == other[i] for i in range(3))

    def __neg__(self):
        return Score(-self[0], -self[1], -self[2])


class Item:
    el: Optional[str] = None
    klass: Optional[str] = None
    identifier: Optional[str] = None
    score: Score
    text: str
    items: Set[str]
    pattern = re.compile(
        "|".join(
            (
                r"(?P<class>\..+?)(?=(?:#|$|\.))",  # Starts with a ., ends before #/$/.
                r"^(?P<el>[^#.]+?)(?:(?=#|$|\.))",  # Start of line, ends with #/$/.
                r"(?P<id>#.+?)(?=(?:\.|$|#))",  # Starts with #, ends with #/$/.
            )
        )
    )

    def __init__(self, text: str):
        """Find all the id, class, and el elements. Build a set of all of the
        elements for matching, and store a score using the count of each"""
        self.text = text
        self.items = set()
        count: Counter = Counter()
        for key, val in self.parse(text):
            self.items.add(val)
            count[key] += 1
            if key == "el":
                self.el = val
            if key == "class":
                # self.class will always be the last class defined
                self.klass = val.strip(".")
            if key == "id":
                self.identifier = val.strip("#")

        self.score = Score(count["id"], count["class"], count["el"])

    @classmethod
    def parse(cls, text) -> Iterable[Tuple[str, str]]:
        """Given a single item from a selector (anything not
        broken by whitespace), parse it into the three types
        of chunk
        :param

        """
        return ((m.lastgroup, m.group()) for m in re.finditer(cls.pattern, text))

    def matches(self, other: "Item"):
        """This is expected to be called by a rule with
        other being an element from the tree. As such,
        we want to check if all of the terms specified
        on `self` are in `other` - other can have extra
        elements that we don't specify so long as it
        isn't missing any
        """
        return self.items.issubset(other.items)


class Selector:
    def __init__(self, text: str):
        self.text = text
        self.items = [Item(item) for item in text.split()]

    def __repr__(self):
        return f"<Selector {self.text}>"

    @property
    def specificity(self) -> Score:
        return reduce(add, self.scores, Score(0, 0, 0))

    @property
    def scores(self):
        yield from (item.score for item in self)

    def matches(self, selector: Union["Selector", str]) -> bool:
        """This is expected to be called by the RULE, passed
        in the comparison element. As such, `other` should be
        much more specific then `self`. What we are actually
        looking for is if all of the elements in `self` are
        contained in `other`. So long as we don't find one that
        is in `self` but not in `other`, return True
        """
        if not isinstance(selector, Selector):
            selector = Selector(selector)
        other = iter(selector)
        # the first item is the actual element- it must match, we
        # cant skip it and go to parents for a match
        must = True
        for item in self:
            try:
                # check the elements in other until we find
                # one that matches this element. If we run
                # out of elements to check, return False
                while not item.matches(next(other)):
                    if must:
                        return False

            except StopIteration:
                return False

            # Once we match the first element, we can look for context matches
            # at any depth
            must = False
        return True

    def __iter__(self):
        # When iterating, go from most immediate to least
        yield from reversed(self.items)

    def __gt__(self, other: "Selector"):
        return self.specificity > other.specificity


class SelectorStorage(SortedKeyList):
    def __init__(self):
        super().__init__(
            key=lambda ruleset: (-ruleset.selector.specificity, -ruleset.order)
        )

    def lookup_rules(self, text):
        while True:
            selector = Selector(text)
            for ruleset in self:
                if ruleset.selector.matches(selector):
                    yield ruleset

            # Handle inheritence, if we cant find any matches for
            # this element, check again with the parent element
            els = text.split()
            if not els:
                return
            text = " ".join(els[:-1])
