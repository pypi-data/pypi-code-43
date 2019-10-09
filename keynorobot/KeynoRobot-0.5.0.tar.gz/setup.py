import pathlib,setuptools,os
#python -m pip install --upgrade pip setuptools wheel
# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
long_description = (HERE / "README.md").read_text()

#with open("README.md", "r") as fh:
#    long_description = fh.read()

setuptools.setup(
    name="KeynoRobot",
    version='0.5.%s' % os.environ.get('TRAVIS_BUILD_NUMBER', 0),
    author="Mehrdad Keyno",
    author_email="hrsk1980@gmail.com",
    description="This is a repository of code, project information and hardware-software design for AI Cognitive maps UAV drone",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mkeyno/KeynoRobot",
    packages=setuptools.find_packages(exclude=("tests",)),
    install_requires=[
          'numpy',
          'opencv-python',
		  'logging','os','asyncio','tensorflow','aiojobs','aiofiles',
		  'json','dotenv','aiohttp','aiohttp_session' ,'serial_asyncio',
      ],
    
#   entry_points={
#        "console_scripts": [
#            "realpython=reader.__main__:main",
#        ]
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)