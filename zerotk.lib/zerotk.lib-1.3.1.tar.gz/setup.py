from setuptools import setup

setup(
    name="zerotk.lib",
    use_scm_version=True,
    author="Alexandre Andrade",
    author_email="kaniabi@gmail.com",
    url="https://github.com/zerotk/zerotk.lib",
    description="Collection of basic Python utilities.",
    long_description="Collection of basic Python utilities.",
    classifiers=[
        "Development Status :: 2 - Pre-Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Natural Language :: English",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
    ],
    keywords="",
    include_package_data=True,
    packages=["zerotk", "zerotk.lib"],
    namespace_packages=["zerotk"],
    install_requires=["ruamel.yaml", "semantic_version", "pathspec"],
    setup_requires=["setuptools_scm"],
    extra_require={
        "testing": ["pytest", "datadiff", "pytest-datadir", "pytest-cov", "codecov"]
    },
    license="MIT license",
)
