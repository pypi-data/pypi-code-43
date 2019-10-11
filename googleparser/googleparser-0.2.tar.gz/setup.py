import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
  name='googleparser',
  packages=['googleparser'],
  version='0.2',
  license='MIT',
  description='Module for parsing google search results without access to Google Search API',
  long_description=long_description,
  long_description_content_type='text/markdown',
  author='Sidorov A.B.',
  author_email='sidan93@gmail.com',
  url='https://github.com/sidan93/googleparser',
  download_url='https://github.com/sidan93/googleparser/archive/v0.1.tar.gz',
  keywords=['google', 'parser', 'search', 'google search', 'google parser', 'googleparser', 'googlesearch'],
  install_requires=[
    'requests',
    'beautifulsoup4',
    'urllib3'

  ],
  classifiers=[
    'Development Status :: 4 - Beta',      # "3 - Alpha", "4 - Beta" or "5 - Production/Stable"
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
