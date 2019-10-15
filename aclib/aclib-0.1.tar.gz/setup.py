from setuptools import setup

setup(name='aclib',
      version='0.1',
      description='The Alphacruncher python library',
      url='https://github.com/datahub-ac/python-connector',
      author='Alphacruncher',
      author_email='support@alphacruncher.com',
      license='MIT',
      packages=['aclib'],
      install_requires=["snowflake-sqlalchemy"],
      zip_safe=False)
