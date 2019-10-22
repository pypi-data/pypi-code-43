import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="zilingo_airflow_utils_test",
    version="1.0.0",
    author="Varnit Khandelwal",
    author_email="varnit.khandelwal13@gmail.com",
    description="Python package which has utility methods for Airflow",
    long_description="This Python package provides the utility methods to access the data from drive, GCS, BigQuery, "
                     "S3 and you can also upload the files on it. Triggering status email for your workflow",
    long_description_content_type="text/markdown",
    url="https://github.com/Varnit-Zilingo/zilingo_airflow_utils_test",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
