import os
import re
import io


class Search(object):
    def __init__(self, parent):
        self.parent = parent
        self.through = self

    def __getattr__(self, key):
        if key not in self.__dict__:
            print("warning you dont choose valid unit")
            return None

    def characters(self):
        self.parent.target_seperators("")
        return self.parent

    def words(self):
        sentence_words = [".", "!", "?"]
        self.parent.target_seperators(
            " ", ",", "\n", *sentence_words
        )
        return self.parent

    def sentence(self):
        self.parent.target_seperators(".", "!", "?")
        return self.parent

    def lines(self):
        paragraph_words = ["\n\n"]
        self.parent.target_seperators(
            "\n", "\r", "\r\n", *paragraph_words
        )
        return self.parent

    def paragraphs(self):
        self.parent.target_seperators("\n\n")
        return self.parent


class Sna(object):
    def __init__(self):
        self.filename = None
        self.entities = dict()
        self.usable_entities = dict()
        self.split_words = None
        self.inplace = False
        self.selected_classes = list()
        self.through = None
        self.default = self.regex

    def __call__(self, *args, **kwargs):
        return self.default(*args, **kwargs)

    def search(self, *args):
        if len(args) == 0:
            self.usable_entities = self.entities.copy()
        else:
            for arg in args:
                if arg in self.entities.keys():
                    self.usable_entities[
                        arg
                    ] = self.entities[arg]

        through = Search(self)
        return through

    def regex(self, regex):
        compilation = re.compile(regex)
        return self.filter(compilation.match)

    def literal(self, literal):
        return self.filter(lambda x: x == literal)

    def filter(self, _filterfunc):
        def decorator(cls):
            if cls.__name__ not in self.entities:
                self.entities[cls.__name__] = list()

            def init(self, match):
                self.match = match

            if type(cls) is not type:
                cls = type(
                    cls.__name__,
                    (),
                    {"__init__": init, "run": cls},
                )
            if (_filterfunc, cls) not in self.entities:
                self.entities[cls.__name__].append(
                    (_filterfunc, cls)
                )
            return cls

        return decorator

    def __getattr__(self, key):

        if key in self.__dict__.keys():
            return self.__dict__[key]
        else:

            def parameter_harvester(*args, **kwargs):
                for cls in self.selected_classes:
                    if hasattr(cls, key):
                        func = getattr(cls, key)
                        func(*args, **kwargs)
                self.selected_classes = list()
                self.usable_entities = dict()

            return parameter_harvester

    def target_seperators(self, *args):
        self.split_words = args
        return self

    def on(self, stg=None, filepath=None):
        new_file = str()
        if self.split_words is None:
            self.lines()

        if filepath is not None:
            if os.path.isfile(filepath):
                filepath = os.path.abspath(filepath)
                with open(filepath, "r") as f:
                    content = f.read()
            else:
                raise Exception(
                    "string or filepath must be provided"
                )

        elif stg is not None and isinstance(stg, str):
            content = stg
        else:
            raise Exception(
                "string or filepath must be provided"
            )

        target = str()

        def process_target(target):
            for (
                cls_name,
                rules,
            ) in self.usable_entities.items():

                for compilation, cls in rules:
                    match = compilation(target)
                    if match is not None:
                        self.selected_classes.append(
                            cls(match)
                        )
            target = str()
            return target

        for char in content:
            target = target + char
            if char in self.split_words:
                target = process_target(target)
        target = process_target(target)
        return self
