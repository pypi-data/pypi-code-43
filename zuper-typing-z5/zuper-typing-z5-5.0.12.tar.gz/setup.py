from setuptools import setup, find_packages


def get_version(filename):
    import ast
    version = None
    with open(filename) as f:
        for line in f:
            if line.startswith("__version__"):
                version = ast.parse(line).body[0].value.s
                break
        else:
            raise ValueError("No version found in %r." % filename)
    if version is None:
        raise ValueError(filename)
    return version

module = 'zuper_typing'
line = 'z5'
package = f'zuper-typing-{line}'
src = 'src'

version = get_version(filename=f"src/{module}/__init__.py")

setup(
    name=package,
    package_dir={"": src},
    packages=find_packages(src),
    version=version,
    zip_safe=False,
    entry_points={
        "console_scripts": [
        ]
    },
    install_requires=[
        "zuper-commons-z5",
        "oyaml",
        "pybase64",
        "PyYAML",
        "validate_email",
        "mypy_extensions",
        "typing_extensions",
        "nose",
        "coverage>=1.4.33",
        "dataclasses",
        "jsonschema",
        "cbor2",
        "numpy",
        "base58",
        "frozendict",
        "pytz",
        "termcolor",
        "numpy",
    ],
)
