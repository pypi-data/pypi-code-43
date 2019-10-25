import setuptools

# with open('README.md', 'r') as f:
#     long_description = f.read()

setuptools.setup(
    name="cryptonite",
    version="0.0.5",
    author="Federico Rizzo",
    author_email="foo@bar.com",
    description="cryptography tools",
    # long_description=long_description,
    long_description_content_type="text/markdown",
    # url="https://github.com/synestematic/cryptonite",
    license="BEER-WARE",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3 :: Only",
        "Development Status :: 3 - Alpha",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS :: MacOS X",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Utilities",
    ],
    install_requires=[
        'bestia',
        'pycrypto',
        # 'gmpy2',
    ],
)
