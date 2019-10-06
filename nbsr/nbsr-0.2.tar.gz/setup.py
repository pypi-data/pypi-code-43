from setuptools import setup

with open("README.txt", "r") as fh:
    long_description = fh.read()

setup(
            name='nbsr',
            version='0.2',
            description='Non-Blocking Stream Reader',
            long_description=long_description,
            url='http://bitbucket.org/netcreator/non-blocking-stream-reader',
            author='Karoly',
            author_email='karolyjozsa@gmail.com',
            license='MIT',
            packages=['nbsr'],
            zip_safe=False,
            classifiers=[
                "Programming Language :: Python :: 2.7",
                "License :: OSI Approved :: MIT License",
                "Operating System :: OS Independent",
            ],
            python_requires='>=2.7',
        )
