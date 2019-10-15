from setuptools import setup


def readme():
    with open('README.rst') as f:
        return f.read()


setup(name='aclib',
      version='0.1.2',
      description='The Alphacruncher python library',
      long_description=readme(),
      url='https://github.com/datahub-ac/python-connector',
      author='Alphacruncher',
      author_email='support@alphacruncher.com',
      license='MIT',
      packages=['aclib'],
      install_requires=["snowflake-sqlalchemy"],
      zip_safe=False)
