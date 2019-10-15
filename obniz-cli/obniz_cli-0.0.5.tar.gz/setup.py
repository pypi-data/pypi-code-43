import setuptools

with open("README.md", "r") as f:
    long_description = f.read()

setuptools.setup(
    name='obniz_cli',
    version='0.0.5',
    description='cli tool for obnizOS setup',
    long_description=long_description,
    long_description_content_type="text/markdown",
    # url='',
    install_requires=["esptool", "requests"],
    py_modules=['obniz_cli'],
    packages=setuptools.find_packages(),
    entry_points={
        "console_scripts": [
            "obniz_cli=obniz_cli:main"
        ]
    }
)