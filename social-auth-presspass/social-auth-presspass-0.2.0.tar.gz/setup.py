import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="social-auth-presspass",
    version="0.2.0",
    author="PressPass Developers",
    author_email="tyler@newscatalyst.org",
    description="PressPass backend and pipelines for the popular Python Social Auth libraries",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/news-catalyst/social-auth-presspass",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)