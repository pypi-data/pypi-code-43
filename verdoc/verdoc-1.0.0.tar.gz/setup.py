"""A setuptools based setup module.

See:
https://packaging.python.org/en/latest/distributing.html
https://github.com/pypa/sampleproject
"""


import codecs
from glob import glob
import os.path

import setuptools  # type: ignore


def read(*parts):
    """Read a file in this repository."""
    here = os.path.abspath(os.path.dirname(__file__))
    with codecs.open(os.path.join(here, *parts), 'r') as file_:
        return file_.read()


ENTRY_POINTS = {
    'console_scripts': [
        'verdoc = verdoc:cli',
        'verdoc-index = verdoc:cli_index',
    ],
}


if __name__ == '__main__':
    setuptools.setup(
        name='verdoc',
        use_scm_version=True,
        description='Deploy references from source control.',
        long_description=read('README.rst'),
        author='David Tucker',
        author_email='david@tucker.name',
        license='LGPLv2+',
        url='https://pypi.org/project/verdoc',
        project_urls={
            'Code': 'https://github.com/dmtucker/verdoc',
            'Issues': 'https://github.com/dmtucker/verdoc/issues',
            'Builds': 'https://travis-ci.com/dmtucker/verdoc',
        },
        package_dir={'': 'src'},
        packages=setuptools.find_packages('src'),
        py_modules=[
            os.path.splitext(os.path.basename(path))[0]
            for path in glob('src/*.py')
        ],
        include_package_data=True,
        setup_requires=['setuptools_scm'],
        python_requires='~= 3.7',
        install_requires=[
            'click ~= 7.0',
            'GitPython ~= 3.0',
            'setuptools ~= 41.2',
        ],
        entry_points=ENTRY_POINTS,
        classifiers=[
            'License :: OSI Approved :: '
            'GNU Lesser General Public License v2 or later (LGPLv2+)',
            'Intended Audience :: End Users/Desktop',
            'Programming Language :: Python :: 3.7',
            'Programming Language :: Python :: 3.8',
            'Development Status :: 3 - Alpha',
        ],
    )
