import setuptools

with open("README.md", "r") as fh:
	long_description = fh.read()

setuptools.setup(
    name="voice_assistant_mm",
    version="0.0.1",
    author="Matthew McCann",
    author_email="matthewmccann41@gmail.com",
    description="A simple module that allows for the quick setup of python Voice Assistants",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/MattCodes03/voice_assist",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)