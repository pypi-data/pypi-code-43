from setuptools import setup

with open("README.rst", "r") as fh:
    long_description = fh.read()

setup(
    name='lazyjson',
    version='0.0.1',
    license='MIT',
    author='Will Stott',
    author_email='willstott101@gmail.com',
    url='https://github.com/willstott101/lazyjson',
    long_description=long_description,
    long_description_content_type="text/x-rst",
    py_modules=['lazyjson'],
    requires=[],
    description='Encode existing JSON strings within new JSON documents efficiently...ish',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    project_urls={
        'Source': 'https://github.com/willstott101/lazyjson',
    },
    python_requires='>=3.5',
)