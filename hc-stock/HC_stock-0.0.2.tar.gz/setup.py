import setuptools
with open("README.md", "r", encoding = 'utf-8') as fh:
    long_description = fh.read()

setuptools.setup(
    name="HC_stock",
    version="0.0.2",
    author="liyifan",
    author_email="liyifan@qq.com",
    description="Test pypi tools.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="http://www.4399.com",
    packages=setuptools.find_packages(),
    license='Apache License',
    install_requires=[
        'matplotlib',
        'bs4',
        'requests',
        'lxml',
        'pandas',
        'tushare'
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)