from setuptools import setup, find_packages

setup(
    name='metascholar',
    version='0.1.0.7',
    packages=find_packages(exclude=['tests*']),
    license='GNU',
    description='A package to retrieve Scholarly Metadata',
    #long_description=open('README.md').read(),
    install_requires=['numpy', 'crossrefapi', 'requests', "fuzzywuzzy"],
    url='https://github.com/ameyakarnad/ameya-sample-package',
    author='Edlab',
    author_email='ameyakarnadbvb@gmail.com'
)
