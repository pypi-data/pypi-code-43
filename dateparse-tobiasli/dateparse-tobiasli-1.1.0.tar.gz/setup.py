import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(name='dateparse-tobiasli',
                 version='1.1.0',
                 description='Package for converting string timestamps into datetimes.',
                 author='Tobias Litherland',
                 author_email='tobiaslland@gmail.com',
                 url='https://github.com/tobiasli/dateparse',
                 packages=setuptools.find_packages(),
                 long_description=long_description,
                 long_description_content_type="text/markdown",
                 classifiers=[
                     "Programming Language :: Python :: 3",
                     "License :: OSI Approved :: MIT License",
                     "Operating System :: OS Independent",
                 ],
                 install_requires=['tregex-tobiasli']
                 )
