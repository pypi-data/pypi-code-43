import setuptools

with open("README.md") as f:
    long_description = f.read()

setuptools.setup(
    name="telegram-bot-sdk",
    version="0.3.4",
    author="myOmikron",
    author_email="kontakt@omikron.pw",
    description="A Implementation of the Telegram Bot API",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/myOmikron/TelegramBotAPI",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
    install_requires=[
        "setuptools",
        "wheel",
        "httpx",
        "jsonpickle"
    ]
)
