from setuptools import setup, find_packages


with open("README.md", "r",encoding='utf-8') as fh:
    long_description = fh.read()

setup(
    name='liquipediapy2',
    version = '1.0.0',
    description= 'api for liquipedia.net',
    author = 'LiuZHolmes',
    author_email = '395637649@qq.com',
    url = 'https://github.com/LiuZHolmes/liquipediapy',
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'beautifulsoup4>=4.6.3',
        'requests>=2.20.1',
        'urllib3>=1.23',
        'lxml>=4.2.4'

    ],
)