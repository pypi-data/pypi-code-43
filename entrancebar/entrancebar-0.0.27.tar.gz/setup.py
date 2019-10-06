import setuptools
import pathlib

setuptools.setup(
    name="entrancebar",
    version="0.0.27",
    author="Chenwe_i_lin",
    author_email="1846913566@qq.com",
    description="importext",
    long_description=pathlib.Path("./description.md").read_text("utf-8") if pathlib.Path("./description.md").exists() else "",
    long_description_content_type="text/markdown",
    url="",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)