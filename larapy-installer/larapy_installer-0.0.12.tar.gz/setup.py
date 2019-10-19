import setuptools
with open("readme.md", "r") as fh:
    long_description = fh.read()
setuptools.setup(
    name='larapy_installer',
    version='0.0.12',
    scripts=['larapy'],
    author="Bedram Tamang",
    author_email="tmgbedu@gmail.com",
    description="Larapy installer for crafting larapy application.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/LaravelPython/installer",
    packages=setuptools.find_packages(),
    install_requires=[
        'cleo',
        'requests',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
