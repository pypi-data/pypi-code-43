import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
        name="flask_2_ui5_py",
        version="0.0.1",
        author="Johannes Heller",
        author_email="strangenewkid@gmail.com",
        description="Utility methods for flask_restful to ui5 messaging ",
        long_description=long_description,
        long_description_content_type="text/markdown",
        url="https://github.com/stopwhispering/flask_2_ui5_py",
        packages=setuptools.find_packages(),
        classifiers=[
            "Programming Language :: Python :: 3",
            "Operating System :: OS Independent",
            ],
        python_requires='>=3.6',
        )
