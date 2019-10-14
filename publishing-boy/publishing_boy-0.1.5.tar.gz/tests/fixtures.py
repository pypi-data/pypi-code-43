import os
from django.core.files.base import ContentFile
from publishing_boy.tests.utils import get_test_storage

temp_dir, storage = get_test_storage()

filename, path = 'test_file.md', 'test_file.md'
content = """
You have to do it Nicky. In order to do that, it’s important to have both overlapping and complementary skills on your team: A good rule of thumb is that any task should have at least two people who can do it, and any two people should have a number of significant tasks where one would obviously be better suited to work on it than another. The former is much more important than the latter, but both are important."""  # noqa

storage.save(filename, ContentFile(content))

obj1 = (
    filename,
    filename,
    os.path.abspath(storage.path(filename)),
    content,
)
