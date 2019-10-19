from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()
setup(
    name='tf_utils',
    version='1.0.2',
    author="Sergiy Isakov",
    author_email="marvine.si@gmail.com",
    description="TensorFlow utils for Generative Adversarial Imitaion Learning",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)

# python setup.py sdist bdist_wheel
# python -m twine upload dist/*