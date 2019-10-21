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
        name = 'ddadevops',
        version = '0.3.0.dev4',
        description = 'tools to support builds combining gopass, terraform, dda-pallet, aws & hetzner-cloud',
        long_description = '',
        author = 'meissa GmbH',
        author_email = 'buero@meissa-gmbh.de',
        license = 'Apache Software License',
        url = 'https://github.com/DomainDrivenArchitecture/dda-devops-build',
        scripts = [],
        packages = ['ddadevops'],
        namespace_packages = [],
        py_modules = [],
        classifiers = [
            'License :: OSI Approved :: Apache Software License',
            'Programming Language :: Python',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.7',
            'Topic :: Software Development :: Build Tools'
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
