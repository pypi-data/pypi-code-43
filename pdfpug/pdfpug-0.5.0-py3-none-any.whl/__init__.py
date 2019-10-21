#  MIT License
#
#  Copyright (C) 2019 Nekhelesh Ramananthan
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED,
#  INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
#  PARTICULAR PURPOSE AND  NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
#  COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN
#  AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
#  WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

__version__ = "0.5.0"

import tempfile
import warnings
from functools import lru_cache
from pathlib import Path
from typing import List, Optional

import jinja2
import weasyprint

from pdfpug.common import BasePugElement, Theme, PageOrientation, PageSize


class PdfReport:
    """
    This is the main class that assembles the elements together to create the
    final PDF output. All the PdfPug elements defined in the :doc:`../modules`
    section need to be added to this class.

    :param Optional[Theme] theme: PDF file theme
    :param bool show_page_numbers: Hide/Show page numbers (defaults to True)
    :param Optional[PageSize] size: Size of pages in the PDF (defaults to A4)
    :param Optional[PageOrientation] orientation: Orientation of pages in PDF (defaults
        to portrait)

    >>> from pdfpug.modules import Header
    >>> from pdfpug import PdfReport
    >>> header = Header('PdfPug Header')
    >>> report = PdfReport()
    >>> report.add_element(header)
    >>> report.generate_pdf('pug-report.pdf')

    PdfPug ships with a predefined themes that can be used to further style
    and modernise the output pdf file.

    >>> from pdfpug.common import Theme
    >>> report = PdfReport(theme=Theme.mood_swing)
    >>> report.generate_pdf('pug-report.pdf')
    """

    BASE_URL = Path(__file__).parent
    SEMANTIC_UI_CSS = BASE_URL / "css" / "semantic.min.css"
    STYLESHEET = BASE_URL / "css" / "style.css"
    THEMES = BASE_URL / "css" / "themes"

    def __init__(self, **kwargs):
        # Private Variables
        self._elements = []
        self._meta_information = None

        # Public Attributes
        self.theme: Optional[Theme] = kwargs.get("theme", None)
        self.size: Optional[PageSize] = kwargs.get("size", PageSize.a4)
        self.show_page_numbers: bool = kwargs.get("show_page_numbers", True)
        self.orientation: Optional[PageOrientation] = kwargs.get(
            "orientation", PageOrientation.portrait
        )

    def add_element(self, element: BasePugElement) -> None:
        """
        Add an element to the PDF file

        :param element: Object instance of the different modules supported by PdfPug
        :raise TypeError: If object instance is not a PdfPug element
        """
        if not isinstance(element, BasePugElement):
            raise TypeError
        self._elements.append(element)

    def add_elements(self, elements: List[BasePugElement]) -> None:
        """
        Add multiple elements in one call to the PDF file

        :param elements: Each element must be an object instance supported by PdfPug
        :raise TypeError: If object instance is not a PdfPug element
        """
        for element in elements:
            if not isinstance(element, BasePugElement):
                raise TypeError
            self._elements.append(element)

    def set_meta_information(
        self,
        title: Optional[str] = None,
        description: Optional[str] = None,
        authors: Optional[List] = None,
        keywords: Optional[List] = None,
    ) -> None:
        """
        Set the document's meta information such as title, description, author etc.

        :param title: Document title
        :param description: Document description
        :param authors: Document authors
        :param keywords: Document keywords
        """
        from pdfpug.modules.metainformation import MetaInformation

        self._meta_information = MetaInformation(
            __version__, title, description, authors, keywords
        )

    @lru_cache(maxsize=1)
    def _get_semantic_ui_css(self):
        with warnings.catch_warnings():
            css = weasyprint.CSS(filename=self.SEMANTIC_UI_CSS)
        return css

    @staticmethod
    def _convert_pug_to_html(pug_file_path: Path) -> str:
        jinja_environment = jinja2.Environment(
            loader=jinja2.FileSystemLoader(
                str(pug_file_path.parent) if pug_file_path.parent else "."
            ),
            extensions=["pypugjs.ext.jinja.PyPugJSExtension"],
        )

        template = jinja_environment.get_template(pug_file_path.name)

        return template.render()

    def _build_stylesheet(self) -> List:
        # Base stylesheet built using the Semantic UI CSS and custom CSS
        stylesheets = [self._get_semantic_ui_css(), self.STYLESHEET]

        # Theme stylesheet
        if self.theme is not None:
            stylesheets.append(self.THEMES / (self.theme.value + ".css"))

        # Set page size and orientation (defaults to A4 portrait)
        customisation_css = f"\n\tsize: {self.size.value} {self.orientation.value};"

        # Show/Hide page numbers
        if self.show_page_numbers:
            customisation_css += (
                "\n\t@bottom-center {"
                '\n\t\tcontent: "Page " counter(page) " of " counter(pages);'
                '\n\t\tfont-family: "Lato";'
                "\n\t}"
            )

        stylesheets.append(weasyprint.CSS(string="@page {" + customisation_css + "\n}"))

        return stylesheets

    def _convert_html_to_pdf(self, html: str, pdf_file_path: str) -> None:
        stylesheets = self._build_stylesheet()
        html_obj = weasyprint.HTML(string=html)
        html_obj.write_pdf(pdf_file_path, stylesheets=stylesheets)

    def generate_pdf(self, pdf_file_path: str) -> None:
        """
        Generate PDF file

        :param pdf_file_path: Absolute path of the PDF file to be created
        """
        from pdfpug.modules import TableOfContents

        pug_file_path = tempfile.mktemp(suffix=".pug")
        with open(pug_file_path, "w+") as pug_file_obj:
            # Compile metadata pug string
            if not self._meta_information:
                self.set_meta_information()
            pug_file_obj.write(self._meta_information.pug + "\n")

            # Compile all elements and get their pug strings
            for element in self._elements:
                if isinstance(element, TableOfContents):
                    element._elements = self._elements
                pug_file_obj.write(element.pug + "\n")

        html = self._convert_pug_to_html(Path(pug_file_path))

        self._convert_html_to_pdf(html, pdf_file_path)
