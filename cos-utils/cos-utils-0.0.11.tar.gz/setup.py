from setuptools import setup

with open('README.md') as readme:
    README = readme.read()

setup(
  name='cos-utils',
  packages=['cos_utils'],
  version='0.0.11',
  license='Apache-2.0',
  description='Cloud Object Storage utility',
  long_description=README,
  long_description_content_type='text/markdown',
  author='Patrick Titzler',
  author_email='ptitzler@us.ibm.com',
  url='https://github.com/CODAIT/cos-utils',
  keywords=['Cloud Object Storage', 'upload', 'download'],
  install_requires=[
                    'ibm-cos-sdk',
                    'requests'
  ],
  entry_points={
    'console_scripts': [
      'upload_files = cos_utils.upload_files:main',
      'download_files = cos_utils.download_files:main',
      'list_files = cos_utils.list_files:main',
      'remove_files = cos_utils.remove_files:main'
    ]
  },
  classifiers=[
    'Development Status :: 4 - Beta',
    'License :: OSI Approved :: Apache Software License',
    'Programming Language :: Python :: 3.6',
    'Programming Language :: Python :: 3.7'
  ],
  zip_safe=True
)
