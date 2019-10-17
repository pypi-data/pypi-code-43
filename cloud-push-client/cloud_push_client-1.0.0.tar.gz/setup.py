import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="cloud_push_client",
    version="1.0.0",
    author="Andreas Dickow",
    author_email="andreas.dickow@biz-factory.de",
    description="A Python client for the Bluemix/IBM push notifications service",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/AndreasDickow/CloudPushNotificationsPythonClient",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.4',
)
