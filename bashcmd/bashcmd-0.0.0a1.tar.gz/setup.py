from distutils.core import setup
setup(
  name = 'bashcmd',
  packages = ['bashcmd'],
  version = '0.0.0a1',
  license='MIT',
  description = 'A bash command wrapper: never need to worry about invoking subprocess to run bash command',
  author = 'Chou Hung-Yi',
  author_email = 'hychou0515@gmail.com',
  url = 'https://gitlab.com/hychou0515/bashcmd',
  download_url = 'https://gitlab.com/hychou0515/bashcmd/-/archive/0.0.0a1/bashcmd-0.0.0a1.tar.gz',
  keywords = ['bash', 'command'],
  install_requires=[],
  classifiers=[
    'Development Status :: 1 - Planning',

    'Intended Audience :: Developers',
    'Topic :: Software Development :: Libraries',
    'Topic :: Utilities',

    'License :: OSI Approved :: BSD License',
    'Operating System :: Unix',

    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
  ],
)
