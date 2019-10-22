from setuptools import find_packages, setup

with open("README.md", "r", encoding="utf-8") as f:
    readme = f.read()

setup(name="swack-multimedia",
      version="0.1.2",
      keywords=["multimedia"],
      description="Multimedia files processing.",
      long_description=readme,
      long_description_content_type="text/markdown",
      license="GNU",
      author="Casen",
      author_email="casen@swack.win",
      packages=find_packages(),
      python_requires=">=3.6",
      install_requires=["numpy>=1.16.0", "opencv-python>=4.0.0"],
      platforms="any",
      url="https://github.com/casen45/swack_multimedia",
      classifiers=[
              "Programming Language :: Python :: 3.6",
              "Programming Language :: Python :: 3.7",
              ],
      zip_safe=False,
      )
