import setuptools
from setuptools import setup


def is_tensorflow_installed():
    """
    detect if tensorflow (no matter CPU or GPU based) installed

    :return: bool, True for tensorflow installed
    """
    import importlib

    try:
        importlib.import_module("tensorflow")
    except ModuleNotFoundError:
        return False

    return True


# without tensorflow by default
install_requires = [
    "numpy",
    "requests",
    "flask",
    "scikit-learn",
    "jsonlines",
    "pconf",
    "tokenizer_tools",
]

if not is_tensorflow_installed():
    install_requires.append("tensorflow")  # Will install CPU based TensorFlow


setup(
    name="ioflow",
    version="0.8.0",
    packages=setuptools.find_packages(),
    url="https://github.com/howl-anderson/ioflow",
    license="Apache 2.0",
    author="Xiaoquan Kong",
    author_email="u1mail2me@gmail.com",
    description="Input/Output abstraction layer for machine learning",
    install_requires=install_requires,
    tests_require=["requests-mock", "pytest", "pytest-datadir"],
)
