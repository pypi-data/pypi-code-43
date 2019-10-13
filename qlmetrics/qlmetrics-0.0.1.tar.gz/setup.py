from setuptools import setup


def get_readme_md_contents():
    with open('README.md') as f:
        long_description = f.read()
        return long_description


#
# TODO: change version to read from __init__.py
setup(
    name="qlmetrics",
    version="0.0.1",
    tests_require=["pytest"],
    packages=[
        'qlmetrics',
    ],
    author="Chris O'Connor",
    long_description=get_readme_md_contents(),
    long_description_content_type='text/markdown',
    author_email="cdoconno@gmail.com",
    description="Metrics tracker",
    license="Apache",
    url="https://github.com/QsonLabs/qlmetrics",
    test_suite="tests",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Framework :: Flake8",
        "Framework :: tox",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: MacOS",
        "Operating System :: Unix",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.7",
    ]
)
