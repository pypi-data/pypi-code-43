from distutils.core import setup
import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()


setup(name='vvar',
      version='0.5',
      description='Virtual user-persistent variables, accessible via an environment object',
      author='Christian Schweigel',
      author_email='',
      url='https://github.com/swip3798/vvar',
      packages=['vvar'],
      long_description = long_description,
      long_description_content_type="text/markdown",
      classifiers=[
          "Programming Language :: Python :: 3",
          "Programming Language :: Python :: 3 :: Only",
          "License :: OSI Approved :: MIT License",
          "Operating System :: OS Independent",
          "Development Status :: 3 - Alpha"
      ]
)