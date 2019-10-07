import pathlib
from setuptools import setup

setup(
    name='wagtailuiplus',
    version='1.3.2',
    description=(
        'This Wagtail app provides several ui improvements to the Wagtail '
        'admin.'
    ),
    long_description=(pathlib.Path(__file__).parent / 'README.md').read_text(),
    long_description_content_type='text/markdown',
    url='https://github.com/david-conde/wagtailuiplus',
    author='David Conde',
    author_email='mail@davidconde.nl',
    license='MIT',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Framework :: Django',
        'Framework :: Django :: 2.2',
        'Framework :: Wagtail',
        'Framework :: Wagtail :: 2',
    ],
    packages=['wagtailuiplus'],
    include_package_data=True,
)
