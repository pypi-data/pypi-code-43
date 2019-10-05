import setuptools

with open("README.md", "r") as fh:
  long_description = fh.read()

setuptools.setup(
  name="podfeed",
  version="1.0.1",
  author="Max Mazzocchi",
  author_email="maxwell.mazzocchi@gmail.com",
  description="A simple podcast feed parser",
  long_description=long_description,
  long_description_content_type="text/markdown",
  url="https://github.com/mmazzocchi/podfeed",
  packages=setuptools.find_packages(exclude=["test", "docs"]),
  classifiers=[
    "Development Status :: 4 - Beta",
    "Programming Language :: Python :: 3",
    "License :: OSI Approved :: MIT License",
    "Operating System :: OS Independent",
    "Intended Audience :: Developers",
    "Topic :: Multimedia :: Sound/Audio",
  ],
  keywords="podcast RSS feed parser",
  install_requires=["feedparser"],
  python_requires=">=3",
)
