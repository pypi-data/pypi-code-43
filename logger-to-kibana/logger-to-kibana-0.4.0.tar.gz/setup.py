import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(
    name='logger-to-kibana',
    version='0.4.0',
    description='Import logger messages from a file and \
                 generates a Kibana Visualization',
    author='Ismael Martinez Ramos',
    author_email='ismaelmartinez@gmail.com',
    url='https://github.com/ismaelmartinez/logger-to-kibana',
    long_description=long_description,
    long_description_content_type="text/markdown",
    entry_points={
        'console_scripts': [
            'logger-to-kibana = main:main'
        ]
    },
    license='MIT',
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=setuptools.find_packages(),
)
