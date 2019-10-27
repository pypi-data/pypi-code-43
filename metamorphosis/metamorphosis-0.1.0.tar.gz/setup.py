from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='metamorphosis',
    version='0.1.0',
    packages=find_packages(),
    url='https://teamworksapp.gitlab.com/jheard/metamorphosis',
    license='MIT',
    author='Jefferson Heard',
    author_email='jheard@teamworks.com',
    description='An opinionated event streaming microframework',
    long_description=long_description,
    long_description_content_type="text/markdown",
    include_package_data=True,
    install_requires=[
        'psutil',
        'click',
        'redis',
        'graphene>=2.1.0',
        'graphql-core>=2.2.0',
        'kafka-python>=1.4.7',
        'msgpack==0.6.2',
        'Werkzeug==0.16.0',
        'Flask>=1.1.0'
    ],
    entry_points='''
        [console_scripts]
        name=metamorphosis.gregor:cli
    ''',
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7'
)
