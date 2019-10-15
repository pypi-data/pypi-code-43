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
        name = 'sparkle-test',
        version = '1.0.0.dev20191015110733',
        description = 'A small and simple base class for fast and clean PySpark unit tests',
        long_description = "\nUnit testing in Spark is made easier with sparkle-test, the settings are tuned for performance and your unit tests\ndon't leave any files in your workspace. There is one convenience method for asserting dataframe equality.\n",
        author = 'Machiel Keizer Groeneveld',
        author_email = 'machielg@gmail.com',
        license = 'GPLv3+',
        url = 'https://github.com/machielg/sparkle-test/',
        scripts = [],
        packages = ['sparkle_test'],
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
        install_requires = ['pandas'],
        dependency_links = [],
        zip_safe = True,
        cmdclass = {'install': install},
        keywords = '',
        python_requires = '',
        obsoletes = [],
    )
