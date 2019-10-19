import setuptools

with open("README.md", "r") as fh:
  long_description = fh.read()

setuptools.setup(
    name="goWSGI",
    version="0.0.1",
    author="SagaraBattousai",
    author_email="jamesafcalo@gmail.com",
    description="A WSGI compatible server",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/SagaraBattousai/goWsgi",
    packages=setuptools.find_packages(),
    classifiers=[
      "Programming Language :: C",
      "Programming Language :: Python :: 3",
      "Programming Language :: Python :: 3.5",
      "Programming Language :: Python :: 3.6",
      "Programming Language :: Python :: 3.7",
      "Programming Language :: Python :: 3.8",
      "Programming Language :: Python :: Implementation :: CPython",
      "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)",
      "Operating System :: Microsoft :: Windows :: Windows 10",
      ],
    python_requires='>=3.5',
)
