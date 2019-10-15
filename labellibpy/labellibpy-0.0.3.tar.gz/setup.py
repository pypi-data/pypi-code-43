import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="labellibpy",
    version="0.0.3",
    author="Mateus M. Souza",
    author_email="mateus.souza@dmcard.com.br",
    description="A small http client for retrieving messages from labelsys.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/gypz/labellib",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=[
        'requests',
    ]
)