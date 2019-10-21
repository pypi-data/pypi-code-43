import setuptools

with open("Readme.md", "r") as fh:
    long_description = fh.read()

# ref: https://packaging.python.org/tutorials/packaging-projects/
setuptools.setup(
    name="presidentsCTF-bot",
    version="0.0.5",
    author="Roy Ragsdale",
    description="Local scoreboard and bot to track the President's Cup.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/royragsdale/presidentsctf-bot",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',

    install_requires=[
        'tabulate',
        'slackclient',
        'tweepy'],

    entry_points={
        'console_scripts': [
        'presidentsCTF=presidentsCTF.main:main',
        ],
    },

    project_urls={
    'Bug Reports': 'https://gitlab.com/royragsdale/presidentsctf-bot/issues',
    'Source': 'https://gitlab.com/royragsdale/presidentsctf-bot/',
    },
)
