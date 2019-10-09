import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name = 'pubg-toolbox',
    version = '0.0.5',
    author = 'Junhan Zhu',
    author_email = 'junhanoct@gmail.com',
    description = 'Simple queries and handles for PUBG data analysis',
    long_description = long_description,
    long_description_content_type = 'text/markdown',
    url = 'https://github.com/junhan-z/pubg-toolbox',
    packages = setuptools.find_packages(),
    classifiers = [
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Topic :: Utilities',
    ],
    python_requires = '>=3',
)
