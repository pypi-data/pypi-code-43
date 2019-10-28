import pathlib
import shutil

import pytest

from django_markdowner.views import MarkdownView


@pytest.fixture(scope='module', autouse=True)
def copy_test_md(md_file: str = './test_md/test.md'):
    """
    This module copies a Test Markdown file.
    """

    if md_file.startswith('./'):
        md_folder = pathlib.Path(__file__).parent
        md_file = md_folder / md_file
    else:
        md_file = pathlib.Path(md_file)
        md_folder = md_file.parent

    if not md_file.exists() and not md_file.is_file():
        pytest.fail(msg='Not markdown file found.')

    template_md = pathlib.Path('./django_markdowner/markdown/')
    template_folder = pathlib.Path('./django_markdowner/templates/')

    # Creates folders
    if not template_md.exists():
        template_md.mkdir()
    if not template_folder.exists():
        template_folder.mkdir()

    # Copies file
    shutil.copy(md_file, template_md)
    template_file = template_folder / pathlib.Path('%s.html' % md_file.stem)
    if not template_file.exists():
        template_file.touch()

    yield

    # Deletes files
    shutil.rmtree(template_md)
    shutil.rmtree(template_folder)


class MarkdownViewForTesting(MarkdownView):
    """
    Test view just to check if everything works correctly.
    """

    template_name = 'test_md/test.html'
    markdown_name = 'test_md/test.md'


def test_testing(rf):
    """
    Checks if markdown was correctly formatted.
    """

    request = rf.get('/')
    view = MarkdownViewForTesting.as_view()(request)
    # Checks for context
    assert all([key in view.context_data for key in ['md', 'raw_md']])
