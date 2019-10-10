from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="ocupgrader",
    use_scm_version=True,
    description=(
        "A tool which wraps the OpenShift command line tools to make upgrades easier"
    ),
    long_description=long_description,
    long_description_content_type="text/markdown",
    license="MIT",
    author="Jan Dobes",
    author_email="jdobes@redhat.com",
    url="https://www.github.com/jdobes/ocupgrader",
    packages=find_packages(),
    keywords=["openshift", "kubernetes"],
    setup_requires=["setuptools_scm"],
    include_package_data=True,
    install_requires=[
    ],
    classifiers=[
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
    ],
    python_requires=">=3.4",
)
