import setuptools

with open('README.md', 'r') as file:
    long_description = file.read()

setuptools.setup(
    name = 'JSONite',
    version = '0.0.3',
    author = 'Chris Byrd',
    author_email = 'christopher.byrd2013@gmail.com',
    description = (
        'Python to Javascript variable converter for the Masonite framework.'
    ),
    long_description = long_description,
    long_description_content_type = 'text/markdown',
    url = 'https://github.com/ChrisByrd14/JSONite',
    packages = setuptools.find_packages(),
    install_requires = ['masonite>=2'],
    classifiers = (
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3 :: Only',
        'Natural Language :: English',
    ),
)

