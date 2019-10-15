#!/usr/bin/env python

from setuptools import setup
from setuptools.command.install import install as _install

class install(_install):
    def pre_install_script(self):
        pass

    def post_install_script(self):
        pass

    def run(self):
        self.pre_install_script()

        _install.run(self)

        self.post_install_script()

if __name__ == '__main__':
    setup(
        name = 'sparkle-hypothesis',
        version = '1.0.0.dev20191015111120',
        description = 'Use the power of hypothesis property based testing in PySpark tests',
        long_description = '\nData heavy tests benefit from Hypothesis to generate your data and desinging your tests. Sparkle-hypothesis makes it \neasy to use Hypothesis strategies to generate dataframes.\n',
        author = 'Machiel Keizer Groeneveld',
        author_email = 'machielg@gmail.com',
        license = 'GPLv3+',
        url = 'https://github.com/machielg/sparkle-hypothesis/',
        scripts = [],
        packages = ['sparkle_hypothesis'],
        namespace_packages = [],
        py_modules = [],
        classifiers = [
            'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
            'Environment :: Console',
            'Programming Language :: Python :: 3.6',
            'Topic :: Software Development :: Testing'
        ],
        entry_points = {},
        data_files = [],
        package_data = {},
        install_requires = [
            'hypothesis',
            'sparkle-session',
            'sparkle-test'
        ],
        dependency_links = [],
        zip_safe = True,
        cmdclass = {'install': install},
        keywords = '',
        python_requires = '',
        obsoletes = [],
    )
