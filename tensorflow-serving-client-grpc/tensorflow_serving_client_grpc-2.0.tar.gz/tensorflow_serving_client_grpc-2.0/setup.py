from os import walk
from pathlib import Path
from setuptools import find_packages, setup


def get_version():
  with open("VERSION", "rt") as f:
    return f.readline().strip()


def init_package():
  package="build/generated/source/proto/main/python"
  for root, dirs, _ in walk(package):
    for d in dirs:
      Path(root, d, "__init__.py").touch()
  return {"packages": find_packages(package),
          "package_dir": {"": package}}


setup(
  name="tensorflow_serving_client_grpc",
  python_requires=">=3.5",
  install_requires=["grpcio", "protobuf"],
  author="Figroc Chen",
  author_email="figroc@gmail.com",
  license="Apache License 2.0",
  url="https://github.com/figroc/tensorflow-serving-client",
  description="A prebuilt tensorflow serving client from the tensorflow serving proto files",
  long_description="""This library does not coexist with tensorflow, tensorflow-serving and
                   tensorflow-serving-api. The official tensorflow-serving-api requires package
                   tensorflow. To eliminate this requirement, this library is setup to generate
                   only neccessary *_pb2.py from the apis of tensorflow_serving.""",
  long_description_content_type="text/plain",
  classifiers=["Development Status :: 5 - Production/Stable",
               "Intended Audience :: Developers",
               "License :: OSI Approved :: Apache Software License",
               "Operating System :: OS Independent",
               "Programming Language :: Python :: 3",
               "Topic :: Scientific/Engineering :: Artificial Intelligence",
               "Topic :: Software Development :: Libraries :: Python Modules"],
  version=get_version(),
  **init_package(),
)
