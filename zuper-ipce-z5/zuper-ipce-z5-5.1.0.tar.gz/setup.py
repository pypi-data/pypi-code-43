from setuptools import find_packages, setup


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


shell_version = get_version(filename="src/zuper_ipce/__init__.py")
line = 'z5'
setup(
    name=f"zuper-ipce-{line}",
    package_dir={"": "src"},
    packages=find_packages("src"),
    version=shell_version,
    zip_safe=False,
    entry_points={
        "console_scripts": [
            # 'zj = zuper_ipce.zj:zj_main',
            "json2cbor = zuper_ipce.json2cbor:json2cbor_main",
            "cbor2json = zuper_ipce.json2cbor:cbor2json_main",
            "cbor2yaml = zuper_ipce.json2cbor:cbor2yaml_main",
        ]
    },
    install_requires=[
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
        "zuper-commons-z5",
        "zuper-typing-z5",
        "frozendict",
        "pytz",
        "termcolor",
        "numpy",
    ],
)
