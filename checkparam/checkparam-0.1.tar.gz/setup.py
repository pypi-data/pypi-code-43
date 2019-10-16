import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
  name='checkparam',
  packages=['checkparam'],
  version='0.1',
  license='MIT',
  description='Module for checking input parameters by type',
  long_description=long_description,
  long_description_content_type='text/markdown',
  author='Sidorov A.B.',
  author_email='sidan93@gmail.com',
  url='https://github.com/sidan93/check_params',
  download_url='https://github.com/sidan93/check_params/archive/v0.1.tar.gz',
  keywords=['check param', 'checkparam', 'params', 'function arguments'],
  install_requires=[
  ],
  classifiers=[
    'Development Status :: 4 - Beta',      # "3 - Alpha", "4 - Beta" or "5 - Production/Stable"
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7',
  ],
)
