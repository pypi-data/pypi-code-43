import shutil
from datetime import datetime, timedelta
from django.core.files.base import ContentFile

from publishing_boy.plugins import (
    title_extractior,
    creation_date,
    modified_date,
    category_extract,
    authors,
)

from tests.fixtures import (
    temp_dir,
    storage,
    filename,
    obj1 as obj,
)

content = """i want to use pelican publishing to generate content.

no styles - simply some non-white background and
some almost-black text - it has to be good for my
eyes. probably some sepia background and some graphite text.

i will use markdown to write
stuff. i will write stuff, then i create a pipleine
in jenkins that will generate title using ntlk,
simply some main words, i will refine this and
use some ai or shit to generate titles
but for now i will have tags
also this will be put into a template of pelican content
so this will be transformation of one set of files
into another set of files and this will transform
into html files"""


def teardown_module():
    shutil.rmtree(temp_dir)


def test_title_extractor():
    """Test title_extractor"""
    f2 = (
        '',
        'file.c',
        '',
        'A b c d',
    )
    f3 = (
        '',
        'a/b/c/file.c',
        '',
        '',
    )
    f4 = (
        '',
        'a/b/c/file.c',
        '',
        content,
    )

    label, r1 = title_extractior(obj)
    _, r2 = title_extractior(f2)
    _, r3 = title_extractior(f3)
    _, r4 = title_extractior(f4)

    assert label == 'title'
    assert r1 == 'You have to do it Nicky'
    assert r2 == 'A b c d ...'
    assert r3 == ''
    assert r4 == 'i want to use pelican publishing to generate content'


def test_creation_date():
    """Test for creation_date"""
    ctime = storage.get_created_time(filename)
    label, result_ctime = creation_date(obj)

    assert label == 'cdate'
    assert ctime == result_ctime
    assert datetime.now() - result_ctime < timedelta(seconds=2)


def test_modified_date():
    """Test getting the modification date"""
    storage.save('test.file', ContentFile('custom contents'))

    mtime = storage.get_modified_time(filename)
    label, result_mtime = modified_date(obj)

    assert label == 'mdate'
    assert mtime == result_mtime

    assert datetime.now() - result_mtime < timedelta(seconds=2)


def test_category_extract():
    """Test category extract"""

    f1 = (
        '',
        'file.c',
        '',
        '',
    )
    f2 = (
        '',
        'a/b/c/file.c',
        '',
        '',
    )
    f3 = (
        '',
        '/file.c',
        '',
        '',
    )

    label, r1 = category_extract(f1)
    _, r2 = category_extract(f2)
    _, r3 = category_extract(f3)

    assert label == 'categories'
    assert r1 == ''
    assert r2 == 'A, B, C'
    assert r3 == ''


def test_authors():

    _label = 'authors'
    _author = 'R.D.X'

    import os
    os.unsetenv('PB_AUTHOR')
    label, author = authors(obj)

    assert label == _label
    assert author == ''

    os.environ['PB_AUTHOR'] = _author
    _, author = authors(obj)
    assert author == _author
