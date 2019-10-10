import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
  name='postgresqlconnector',
  packages=['postgresqlconnector'],
  version='0.6',
  license='MIT',
  description='A small module for working quickly with the PostgreSQL',
  long_description=long_description,
  long_description_content_type='text/markdown',
  author='Sidorov A.B.',
  author_email='sidan93@gmail.com',
  url='https://github.com/sidan93/postgresql_connector',
  download_url='https://github.com/sidan93/postgresql_connector/archive/v0.6.tar.gz',
  keywords=['Postgre', 'PostgreSQL', 'connector', 'postgresqlconnection', 'postgresql connector'],
  install_requires=[
    'psycopg2',
    'psycopg2-binary'
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
