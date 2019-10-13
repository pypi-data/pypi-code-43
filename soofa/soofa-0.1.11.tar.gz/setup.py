from distutils.core import setup

try:
  with open("README.rst", "r") as fh:
    long_description = fh.read()
except IOError:
  long_description = "Soofapay python intergration"

setup(
  name = 'soofa',
  packages = ['soofa'],
  version = '0.1.11',
  license='MIT',
  description = 'Python package to simplify integration to soofapay',
  long_description=long_description,
  author = 'Soofapay Team',
  author_email = 'info@soofapay.com',
  url = 'https://github.com/soofapay/python-soofa',
  download_url = 'https://github.com/soofapay/python-soofa/archive/v0.1.11-beta.tar.gz',
  keywords = ['soofa', 'soofapay', 'pay', "python"],
  install_requires=[
          'requests',
      ],
  classifiers=[
    'Development Status :: 4 - Beta',      # Chose either "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state of your package
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
  ],
)