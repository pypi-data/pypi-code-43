import os
from publishing_boy.publishing_boy import transform
from tests.fixtures import ContentFile, get_test_storage, filename, content
import shutil


def test_transform():
    global filename, content
    temp_dir, storage = get_test_storage()

    storage.save(filename, ContentFile(content))

    obj = (filename,
       filename,
       os.path.abspath(storage.path(filename)),
       content,)

    from publishing_boy.plugins import (
        authors,
        title_extractior,
        creation_date,
        modified_date,
        category_extract,
        content_function,
    )

    result = transform(obj)

    filename, filepath, abspath, content = obj
    r_f, r_fp, r_abs, f_content = result
    assert r_f == filename
    assert r_fp == filepath
    assert r_abs == abspath

    assert f_content.find('Title:') > 0
    assert f_content.find('Date:') > 0
    assert f_content.find('Modified:') > 0
    assert f_content.find('Category:') > 0
    assert f_content.find('Authors:') > 0

    shutil.rmtree(temp_dir)
