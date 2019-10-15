import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
      name='rmi_qb_sdk',
      version='0.3.2',
      description='Reading & Math Inc Python SDK for Quick Base',
      long_description=long_description,
      long_description_content_type="text/markdown",
      url='https://github.com/ReadingandMath/Quickbase-Python-SDK',
      author='Kevin Connor',
      author_email='kevin.connor@servetogrow.org',
      license='MIT',
      packages=setuptools.find_packages(),
      zip_safe=False,
      classifiers=[
        "Programming Language :: Python :: 3",
      ],
)
