import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='logger-to-kibana',
    version='0.0.7',
    description='Import logger messages from a file and \
                 generates a Kibana Visualisation',
    author='Ismael Martinez Ramos',
    author_email='ismaelmartinez@gmail.com',
    long_description=long_description,
    long_description_content_type="text/markdown",
    entry_points={
        'console_scripts': [
            'logger-to-kibana = main:main'
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=setuptools.find_packages(),
)
