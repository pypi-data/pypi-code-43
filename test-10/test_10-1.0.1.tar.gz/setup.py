import setuptools

with open("README.md", "r") as fh:
    my_description = fh.read()


setuptools.setup(
    name="test_10",
    version="1.0.1",
    author="Le Quang Nhat",
    author_email="nhat.le@f4.intek.edu.vn",
    description="Sprite detection package",
    license='MIT',
    copyright='Copyright (C) 2019, Intek Institute - Master Nhat',
    install_requires=['numpy', 'pillow'],
    long_description=my_description,
    long_description_content_type="text/markdown",
    url="https://github.com/intek-training-jsc/sprite-detection-masternhat",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)