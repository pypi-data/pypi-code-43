from pathlib import Path

from setuptools import (find_packages,
                        setup)

import dendroid

project_base_url = 'https://github.com/lycantropos/dendroid/'

setup_requires = [
    'pytest-runner>=4.2',
]
install_requires = Path('requirements.txt').read_text()
tests_require = Path('requirements-tests.txt').read_text()

setup(name=dendroid.__name__,
      packages=find_packages(exclude=('tests', 'tests.*')),
      version=dendroid.__version__,
      description=dendroid.__doc__,
      long_description=Path('README.md').read_text(encoding='utf-8'),
      long_description_content_type='text/markdown',
      author='Azat Ibrakov',
      author_email='azatibrakov@gmail.com',
      classifiers=[
          'Development Status :: 3 - Alpha',
          'Intended Audience :: Developers',
          'License :: OSI Approved :: MIT License',
          'Programming Language :: Python :: 3.5',
          'Programming Language :: Python :: 3.6',
          'Programming Language :: Python :: 3.7',
      ],
      license='MIT License',
      url=project_base_url,
      download_url=project_base_url + 'archive/master.zip',
      python_requires='>=3.5',
      setup_requires=setup_requires,
      install_requires=install_requires,
      tests_require=tests_require)
