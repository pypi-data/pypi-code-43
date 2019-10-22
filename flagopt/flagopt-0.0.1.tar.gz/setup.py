import setuptools

with open('README.md') as file:

    readme = file.read()

name = 'flagopt'

version = '0.0.1'

author = 'Exahilosys'

url = f'https://github.com/{author}/{name}'

setuptools.setup(
    name = name,
    version = version,
    url = url,
    packages = setuptools.find_packages(),
    license = 'MIT',
    description = 'Command line based argument parse framework.',
    long_description = readme,
    long_description_content_type = 'text/markdown',
    install_requires = [
        'multidict'
    ]
)
