from distutils.core import setup
setup(
  name = 'cerberusctl',
  packages = ['cerberusctl'],
  scripts = ['bin/cerberus'],
  version = '0.0.11',
  license='MIT',
  description = 'The cli for cerberus secrets manager',
  author = 'Caduedu14',
  author_email = 'carlosedu.dev@gmail.com',
  url = 'https://github.com/Caduedu14/cerbeructl',
  download_url = 'https://github.com/Caduedu14/cerberusctl/archive/v0.0.11.tag.gz',
  keywords = ['PASSWORD', 'SECRET', 'VAULT'],
  install_requires=[
      'Click',
      'PyInquirer',
      'pyperclip',
      'clipboard'
      ],
  classifiers=[
    'Development Status :: 3 - Alpha',
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
  ],
)
