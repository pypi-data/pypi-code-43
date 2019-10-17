import setuptools


try:
    # for pip >= 10
    from pip._internal.req import parse_requirements
except ImportError:
    # for pip <= 9.0.3
    from pip.req import parse_requirements


def load_requirements(fname):
    reqs = parse_requirements(fname, session="test")
    return [str(ir.req) for ir in reqs]


def long_description(fname):
    with open(fname) as f:
        return f.read()


setuptools.setup(
    name='squat',
    version='1.0.3',
    scripts=[],
    author="Binay Kumar Ray",
    author_email="binayray2009@gmail.com",
    description="SQUAT",
    long_description=long_description('README.md'),
    long_description_content_type="text/markdown",
    url="https://github.com/binayr/SQUAT.git",
    packages=setuptools.find_packages(),
    include_package_data=True,
    install_requires=load_requirements('requirements.txt'),
    dependency_links=[
        "https://github.com/explosion/spacy-models/releases/tag/en_core_web_sm-2.1.0"
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    entry_points={
          'console_scripts': [
              # add cli scripts here in this form:
              'squat=squat.cli:main'
          ],
      }
)
