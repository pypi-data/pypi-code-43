import inspect
import pathlib

from django.core.exceptions import ImproperlyConfigured
from django.views.generic import TemplateView

from django_markdowner.templatetags.md_tags import to_markdown


class MarkdownView(TemplateView):
    """
    Renders a Markdown file into a Django Template.
    """

    markdown_name = None

    def get_context_data(self, **kwargs):
        """
        Adds markdown formatted to the context as `md`.
        """

        context = super().get_context_data(**kwargs)
        context['raw_md'] = self.get_markdown_text()
        context['md'] = self.parse_markdown()
        return context

    def get_markdown_names(self) -> list:
        """
        Returns a list of markdown files to be used for the request.
        """

        if self.markdown_name is None:
            raise ImproperlyConfigured("'markdown_name' is not defined.")
        return [self.markdown_name]

    def get_markdown_files(self, md_file: str) -> pathlib.Path:
        """
        Returns the file of the markdown as :class:`pathlib.Path`.
        """

        folder = pathlib.Path(inspect.getfile(self.__class__)).parent
        md_file = folder / md_file

        if not md_file.exists() or not md_file.is_file():
            raise ImproperlyConfigured("One of the Markdown files does not exist or is not a file.")

        return md_file

    def get_markdown_text(self) -> str:
        """
        Gets markdown text.
        """

        md_files = list(map(self.get_markdown_files, self.get_markdown_names()))
        markdown_text = ''

        for md_file in md_files:
            markdown_text += md_file.read_text() + '\n'

        return markdown_text

    def parse_markdown(self) -> str:
        """
        Transform Raw Markdown to HTML.
        """

        return to_markdown(self.get_markdown_text())
