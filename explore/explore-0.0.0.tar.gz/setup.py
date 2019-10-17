import setuptools

with open('README.md') as file:

    readme = file.read()

name = 'explore'

version = '0.0.0'

author = 'Exahilosys'

url = f'https://github.com/{author}/{name}'

setuptools.setup(
    name = name,
    version = version,
    url = url,
    packages = setuptools.find_packages(),
    license = 'MIT',
    description = 'Value scoring and best match picking.',
    long_description = readme,
    long_description_content_type = 'text/markdown'
)
