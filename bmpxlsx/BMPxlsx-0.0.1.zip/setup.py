from distutils.core import setup


setup(
  name = 'BMPxlsx',
  packages = ['BMPxlsx'],
  version = '0.0.1',
  license='MIT',
  description = 'The library takes a dictionary of form {Sheet: {Cell: Value}} and updates the specified Excel file accordingly.',
  author = 'Mike Campagna',
  author_email = 'msc94@drexel.edu',
  url = 'https://github.com/TheAcademyofNaturalSciences/BMPxlsx',
  download_url = 'https://github.com/TheAcademyofNaturalSciences/BMPxlsx/archive/v_001.tar.gz',
  keywords = ['Excel', 'Write', 'XLSX', 'BMP'],
  install_requires=[
          'openpyxl',
      ],
  classifiers=[
    'Development Status :: 3 - Alpha', # "3 - Alpha", "4 - Beta" or "5 - Production/Stable" as the current state
    'Intended Audience :: Developers',
    'Topic :: Software Development :: Build Tools',
    'License :: OSI Approved :: MIT License',
    'Programming Language :: Python :: 2.7'
  ],
)
