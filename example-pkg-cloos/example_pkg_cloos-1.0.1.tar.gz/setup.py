import setuptools

with open("README.rst") as f:
    long_description = f.read()

setuptools.setup(
    name="example_pkg_cloos",
    author="Christian Loos",
    author_email="cloos@netsandbox.de",
    description="A example package to learn and test Python packaging.",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    license="MIT",
    url="https://github.com/cloos/python_example_pkg_cloos",
    packages=setuptools.find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Operating System :: POSIX",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Topic :: Software Development",
        "Topic :: Software Development :: Build Tools",
        "Topic :: Software Development :: Libraries",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Testing",
    ],
    python_requires=">=2.7, !=3.0.*, !=3.1.*, !=3.2.*, !=3.3.*",
    setup_requires=["setuptools_scm"],
    use_scm_version=True,
    install_requires=[
        "click>=4.0",
    ],
    entry_points={
        "console_scripts": "example-pkg-cloos=example_pkg_cloos.cli:main"
    },
)
