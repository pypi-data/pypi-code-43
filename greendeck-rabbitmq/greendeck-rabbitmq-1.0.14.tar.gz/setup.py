import setuptools

with open("README.md", "r") as f:
    long_description = f.read()


setuptools.setup(
    name="greendeck-rabbitmq",
    version="1.0.14",
    author="chandan mishra",
    author_email="chandan.mishra@greendeck.co",
    description="Greendeck rabbitmq package",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/IIITian-Chandan/greendeck-rabbitmq.git",
    packages=['greendeck_rabbitmq', 'greendeck_rabbitmq.src', 'greendeck_rabbitmq.src.rabbitmq'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        'pika', 'tqdm'
    ],
    include_package_data=True,
    zip_safe=False
)
