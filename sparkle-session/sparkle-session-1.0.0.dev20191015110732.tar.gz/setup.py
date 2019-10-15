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
        name = 'sparkle-session',
        version = '1.0.0.dev20191015110732',
        description = 'Spark Session and DataFrame extensions',
        long_description = 'Common patterns and often used code from dozens of pyspark projects available at your fingertips',
        author = 'Machiel Keizer Groeneveld',
        author_email = 'machielg@gmail.com',
        license = '',
        url = 'https://github.com/machielg/sparkle-session/',
        scripts = [],
        packages = ['sparkle_session'],
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
        install_requires = [],
        dependency_links = [],
        zip_safe = True,
        cmdclass = {'install': install},
        keywords = '',
        python_requires = '',
        obsoletes = [],
    )
