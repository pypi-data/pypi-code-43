import setuptools

with open("README.md", "r") as f:
    long_description = f.read()

with open('requirements.txt') as req:
    requirements = list(filter(None, [x if 'github.com' not in x else None for x in req.read().split('\n')]))

with open('requirements.txt') as req:
    dependencies = list(filter(None, [x if 'github.com' in x else None for x in req.read().split('\n')]))

EXCLUDE_FROM_PACKAGES = ['docs', 'tests*']

setuptools.setup(
    name="metric_builder",
    version="0.0.1",
    author="Philip Perold",
    author_email="philip@spatialedge.co.za",
    description="Utility for building templated metric extraction queries that can be traversed through time.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    packages=setuptools.find_packages(exclude=EXCLUDE_FROM_PACKAGES),
    install_requires=requirements,
    dependency_links=dependencies,
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3',
        'Topic :: Utilities'
    ],
    include_package_data=True
)
