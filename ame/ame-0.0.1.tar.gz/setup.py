from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='ame',
    version='0.0.1',
    packages=find_packages(exclude=['tests',]),
    url='https://github.com/lorranfoliveira/ame',
    license='MIT',
    author='Lorran Ferreira Oliveira',
    author_email='lorranfoliveira@gmail.com',
    description='Biblioteca para análise matricial de estruturas planas pelo método dos deslocamentos.',
    long_description=long_description,
    install_requires=['numpy == 1.17.2',
                      'scipy == 1.3.1',
                      'PTable == 0.9.2',
                      'matplotlib == 3.1.1'],
    classifiers=('License :: OSI Approved :: MIT License',
                 'Programming Language :: Python :: 3.7',
                 'Operating System :: OS Independent')
)
