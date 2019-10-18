import jinja2
import yaml
from docutils.parsers.rst import Parser as RestructuredTextParser

try:
    from recommonmark.parser import CommonMarkParser as MarkdownParser
except ImportError:
    MarkdownParser = None

__all__ = ["JinjaRestructuredTextParser"]


def preprocess(inputstring):
    if "\n---\n" in inputstring:
        metadata, text = inputstring.split("\n---\n", 1)
        data = yaml.safe_load(metadata)
    else:
        data = {}
        text = inputstring
    template = jinja2.Template(text)
    return template.render(**data)


class JinjaRestructuredTextParser(RestructuredTextParser):
    supported = ("jrst",)

    def parse(self, inputstring, document):
        return super().parse(preprocess(inputstring), document)


if MarkdownParser:
    __all__.append("JinjaMarkdownParser")

    class JinjaMarkdownParser(MarkdownParser):
        supported = ("jmarkdown",)

        def parse(self, inputstring, document):
            return super().parse(preprocess(inputstring), document)


else:
    JinjaMarkdownParser = None
