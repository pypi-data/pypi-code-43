import setuptools

with open('README.md') as f:
    long_description = f.read()

setuptools.setup(
    name='countfiles',
    version='0.3.4',
    author='Aiden Blishen Cuneo',
    author_email='aidencuneo@gmail.com',
    description='A simple module to count or list the attributes of files in a directory.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/pypa/sampleproject',
    packages=setuptools.find_packages(),
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
    python_requires='>=3.1',
)
