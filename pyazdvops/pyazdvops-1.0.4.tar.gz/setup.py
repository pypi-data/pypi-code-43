import setuptools

setuptools.setup(
  name = 'pyazdvops',
  version = '1.0.4',
  description = 'Library for Azure DevOps API for Python',
  author = 'Faizal Sidek',
  author_email = 'faizal.sidek@gmail.com',
  license = 'Free for non-commercial use',
  packages = ['azdvop'],
  zip_safe = False,
  install_requires = ['requests','redis'],
  url = 'https://github.com/rockraft7/pyazdevops',
  keywords = ['Azure', 'DevOps', 'Python', 'API'],
  classifiers = [
    'Development Status :: 3 - Alpha', 
    'Intended Audience :: Developers', 
    'Topic :: Software Development :: Libraries',
    'License :: Free for non-commercial use',
    'Natural Language :: English',
    'Programming Language :: Python :: 2.7'
  ]
)
