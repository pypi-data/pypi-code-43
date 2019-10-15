from setuptools import setup, find_packages
import jcopdl

with open("README.md", "r") as f:
    description = f.read()

setup(
    name="jcopdl",
    version=jcopdl.__version__,
    author="Wira Dharma Kencana Putra",
    author_email="wiradharma_kencanaputra@yahoo.com",
    description="J.COp DL is a deep Learning package to complement pytorch workflow",
    long_description=description,
    long_description_content_type="text/markdown",
    python_requires=">=3.6.7",
    install_requires=['torch', 'numpy', 'pandas', 'matplotlib', 'pillow'],
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "Intended Audience :: Developers",
        "Intended Audience :: Education",
        "Intended Audience :: Information Technology",
        "Intended Audience :: Science/Research",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Natural Language :: Indonesian",
        "Natural Language :: English"
    ],
    keywords="deep learning dl jcop indonesia",
    url="https://github.com/WiraDKP/jcopdl"
)