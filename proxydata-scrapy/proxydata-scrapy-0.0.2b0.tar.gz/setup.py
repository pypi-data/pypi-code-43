import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="proxydata-scrapy",
    version="0.0.2b",
    author="nekidaem",
    author_email="order@nekidaem.ru",
    description="Middleware for proxying scrapy requests through the service proxyfordevelopers.com",
    long_description=long_description,
    long_description_content_type="text/markdown",
    # url="https://gitlab.com/mkispb/proxydata-scrapy",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)