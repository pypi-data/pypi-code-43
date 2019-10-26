import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="saywhen",
    description="Send notifications when command line job finishes",
    version="0.0.2",
    author="Yunqing Gong",
    author_email="gongyq10@gmail.com",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yunqing/saywhen",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    packages=['saywhen'],
    package_data={
        'saywhen': [
            'audio/*'
            ]
        },
    include_package_data=True,
    scripts=['scripts/saywhen'],
    python_requires='>=3.5',
)
