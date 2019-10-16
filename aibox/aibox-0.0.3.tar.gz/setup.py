from setuptools import setup, find_packages

setup(
      name='aibox',
      version='0.0.3',
      zip_safe = False,
      long_description='ai code library for rucaibox group',
      license='RUC AI Box License',

      author='Junyi Li',
      author_email='cheneyjunyi@gmail.com',

      maintainer='Junyi Li',
      maintainer_email='cheneyjunyi@gmail.com',

      packages=find_packages(),
      include_package_data=True,
      platforms="any",
      install_requires=["requests", "re", "nltk", "string"]
)