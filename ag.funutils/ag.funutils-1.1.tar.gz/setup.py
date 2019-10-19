import setuptools

with open('README.md', 'r') as readme:
    long_description = readme.read()

setuptools.setup(
    name='ag.funutils',
    version='1.1',
    author='Austin Garrard',
    author_email='austin.w.garrard@gmail.com',
    description='Fun functional utilities',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/austin-garrard/ag.funutils',
    packages=['ag.funutils']
)
