import codecs

import setuptools

import pycleanarch

# with open("README.md", "r", 'utf-8') as fh:
#     long_description = fh.read()

with codecs.open('README.md', 'r', 'utf-8') as fd:

    setuptools.setup(
        name="pycleanarch",
        version=pycleanarch.__version__,
        author="Wallace Silva",
        author_email="contato@wallacesilva.com",
        maintainer='Wallace Silva',
        license='MIT License',
        maintainer_email='contato@wallacesilva.com',
        description="A simple Python toolkit to work with Clean Architecture for Web ",
        long_description=fd.read(),
        long_description_content_type="text/markdown",
        url="https://github.com/wallacesilva/pycleanarch",
        packages=setuptools.find_packages(),
        classifiers=[
            "Programming Language :: Python :: 3",
            "License :: OSI Approved :: MIT License",
            'Intended Audience :: Developers',
            'Topic :: Software Development :: Libraries :: Python Modules',
            'Topic :: Software Development :: Quality Assurance',
        ],   
    )