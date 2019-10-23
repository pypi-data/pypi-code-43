import setuptools

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='monodrive',
    version='0.0.0',
    author='monoDrive',
    author_email='devin@monodrive.io',
    description='monodrive pip placeholder',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com',
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ]
)
