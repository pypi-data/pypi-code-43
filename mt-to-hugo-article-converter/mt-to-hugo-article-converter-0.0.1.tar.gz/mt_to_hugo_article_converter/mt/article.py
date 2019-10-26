import re
from functools import reduce
from .attribute import Author, Title, Basename, Status, PrimaryCategory, Category, Date, Tags, Body, ExtendedBody, Keywords


class Article:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.attributes = [
            Author(),
            Title(),
            Basename(),
            Status(),
            PrimaryCategory(),
            Category(),
            Date(),  # TODO: date fmt
            Tags(),
            Body(),
            ExtendedBody(),
            Keywords()
        ]

    def fullfilled(self):
        filterd = filter(lambda attr: attr.is_open()
                         or attr.is_empty(), self.attributes)
        not_filled = list(filterd)
        return len(not_filled) == 0

    def append_line(self, line):
        self.attributes = list(
            map(lambda record: record.set(line), self.attributes))
        return self.fullfilled()
