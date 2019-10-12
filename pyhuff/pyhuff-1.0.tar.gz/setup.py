import setuptools

with open('DESCRIPTION.md', 'r') as readme:
  long_description = readme.read()

with open('requirements.txt', 'r') as requirements_file:
  requirements_text = requirements_file.read()

requirements = requirements_text.split()

setuptools.setup(
    name='pyhuff',
    version='1.0',
    description='This is a huffman code compressor',
    url='https://github.com/projeto-de-algoritmos-2019-2/project-3-huffman-code-cli',
    author='Victor Moura',
    author_email='victor_cmoura@hotmail.com',
    license='GPL-3.0',
    packages=setuptools.find_packages(),
    zip_safe=False,
    long_description_content_type="text/markdown",
    long_description=long_description,
    install_requires=requirements,
    scripts=['pyhuff/bin/pyhuff']
)