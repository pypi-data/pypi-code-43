import os

import black
from mistune import Renderer


class CodeFormatter(Renderer):
    def __init__(self, line_break=os.linesep, **kwargs):
        super().__init__(**kwargs)
        self.sep = line_break

    def header(self, text, level, raw=None):
        return f"{'#'*level} {text}" + self.sep * 2

    def codespan(self, text):
        return f'`{text}`'

    def linebreak(self):
        return self.sep

    def newline(self):
        return self.sep

    def list_item(self, text):
        return f'- {text}' + self.sep

    def list(self, body: str, ordered=True):
        if ordered:
            b = ''
            for i, line in enumerate(body.splitlines()):
                real_line_content = line.split('- ', 1)[-1]
                b += f'{i+1}. {real_line_content}' + self.sep
            body = b
        return body + self.sep

    def paragraph(self, text):
        return text + self.sep * 2

    def block_code(self, code, lang=''):
        if lang == 'python':
            try:
                code = black.format_str(code, 80)[:-1]  # remove tailing blank line
            except black.InvalidInput:
                pass  # noqa
        return f"""```{lang}""" + self.sep + code + self.sep + '```' + self.sep * 2

    def link(self, link, title, text):
        return f'[{text}]({link})'

    def autolink(self, link, is_email=False):
        return f'<{link}>'

    def image(self, src, title, text):
        return f'![{text}]({src})'
