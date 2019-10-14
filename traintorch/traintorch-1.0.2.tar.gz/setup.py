import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="traintorch",
    version="1.0.2",
    author="Rouzbeh Afrasiabi",
    author_email="rouzbeh.afrasiabi@gmail.com",
    description="Package for live visualization of metrics during training of a machine learning model",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/rouzbeh-afrasiabi/traintorch",
    download_url="https://github.com/rouzbeh-afrasiabi/traintorch/archive/v.1.0.2-alpha.tar.gz",
    install_requires=[
    'numpy>=1.17.2',
    'pandas>=0.25.1',
    'matplotlib>=3.1.1',
    'pycm>=2.2',
    ],
    keywords = ['training', 'visualization', 'loss','plot','live','jupyter notebook', 'matplotlib'],
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
    ],
)
