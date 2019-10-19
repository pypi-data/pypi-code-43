import setuptools
import pipfile

pf = pipfile.load('./Pipfile')

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    author="ntthanhvy",
    author_email="vy.nguyen@f4.intek.edu.vn",
    version="1.0.0",
    name="spriteutils_7",
    license='MIT',
    description="A program to detect soem sprite in an image",
    long_description=long_description,
    url="https://github.com/intek-training-jsc/sprite-detection-ntthanhvy",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: POSIX :: Linux"
    ],
    python_requires='>=3.6',
    install_requires=['Pillow', 'numpy']
)