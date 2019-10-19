import setuptools

with open('requirements.txt') as f:
    required = f.read().splitlines()

setuptools.setup(
    name="politweet",
    version="0.0.2",
    author="",
    author_email="author@example.com",
    description="library for processing italian political tweets",
    packages=setuptools.find_packages(),
    install_requires = required,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
