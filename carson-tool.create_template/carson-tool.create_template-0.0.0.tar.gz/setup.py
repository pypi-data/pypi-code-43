from distutils.core import setup
from pathlib import Path

VERSION_NUMBER = '0.0.0'
LIST_SCRIPTS = [str(script_file) for script_file in Path('Scripts').glob('*.*')]
GITHUB_URL = 'https://github.com/CarsonSlovoka/carson-tool.create_template'

with open('README.rst', encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='carson-tool.create_template',
    version=VERSION_NUMBER,  # x.x.x.{dev, a, b, rc}
    packages=['Carson', 'Carson/Tool', 'Carson/Tool/CreateTemplate', ],
    package_data={'Carson/Tool/CreateTemplate': ['template/*.template']},
    license="Apache-2.0",

    author='Carson',
    author_email='jackparadise520a@gmail.com',

    scripts=LIST_SCRIPTS,  # create_template.bat

    install_requires=['colorama', ],

    url=GITHUB_URL,

    description='File templates are specifications of the default contents to be generated when creating a new file.',
    long_description=long_description,
    long_description_content_type='text/x-rst',  # text/markdown
    keywords=['templates'],

    download_url=f'{GITHUB_URL}/tarball/v{VERSION_NUMBER}',
    python_requires='>=3.6.2,',

    zip_safe=False,
    classifiers=[  # https://pypi.org/classifiers/
        'Topic :: System :: Filesystems',
        'Natural Language :: Chinese (Traditional)',
        'Natural Language :: English',
        'Operating System :: Microsoft',
        'Development Status :: 5 - Production/Stable',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ]
)
