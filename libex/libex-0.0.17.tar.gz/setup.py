import setuptools

exec(open('libex/__init__.py').read())

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="libex",
    version=__version__,
    author="dozenc",
    author_email="dozenc@outlook.com",
    description="Crypto Currency Exchange Library",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/dozenc/libex",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.5, <4',
    install_requires=['requests==2.22.0', 'iso8601==0.1.12','websockets>=7.0', 'python_dateutil==2.8.0' ],  # Optional
    project_urls={  # Optional
        'Bug Reports': 'https://gitlab.com/dozenc/libex',
        'Funding': 'https://gitlab.com/dozenc/libex',
        'Say Thanks!': 'https://gitlab.com/dozenc/libex',
        'Source': 'https://gitlab.com/dozenc/libex',
    },
)
