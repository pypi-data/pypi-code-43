from distutils.core import setup

setup(
    name='pytf2',
    version='3.6.5',
    packages=['pytf2'],
    url='https://github.com/mninc/pytf',
    license='MIT',
    author='manic',
    author_email='manicminer106@gmail.com',
    description='An API wrapper for everything TF2-related',
    install_requires=['requests', 'lxml', 'aiohttp', 'cfscrape', 'AdvancedHTMLParser'],
    python_requires='>=3'
)
