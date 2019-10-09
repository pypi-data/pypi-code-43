import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="traintorch",
    version="1.0.1",
    author="Rouzbeh Afrasiabi",
    author_email="rouzbeh.afrasiabi@gmail.com",
    description="Package for live visualization of metrics during training of a machine learning model",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/rouzbeh-afrasiabi/traintorch",
    download_url="https://github.com/rouzbeh-afrasiabi/traintorch/archive/1.0.1-alpha.1.tar.gz",
    install_requires=[
    'numpy',
    'pandas',
    'matplotlib',
    'ipython' 
    ],
    keywords = ['training', 'visualization', 'loss','plot','live','jupyter notebook', 'matplotlib'],
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
