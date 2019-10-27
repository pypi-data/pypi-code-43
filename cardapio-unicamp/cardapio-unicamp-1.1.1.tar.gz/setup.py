import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="cardapio-unicamp",
    version="1.1.1",
    author="Nícolas F. R. A. Prado",
    author_email="nfraprado@protonmail.com",
    description="A menu fetcher for Unicamp's restaurant",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/nfraprado/cardapio-unicamp",
    packages=setuptools.find_packages(),
    entry_points={
        'console_scripts': [
            'cardapio-unicamp=cardapio_unicamp:main'
        ]
    },
    python_requires='>=3',
    install_requires=[
        'beautifulsoup4', 'requests'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
)
