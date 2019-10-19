import os
class Package:
	def __init__(self, Name , Author, Author_email, Version, Main_File_Path, Project_Description, Homepage, README=""):
		self.Name = Name
		self.Author = Author
		self.Author_email = Author_email
		self.Version = Version
		self.Project_Description = Project_Description
		self.README = README 
		self.Homepage = Homepage
		self.Main_File_Path = Main_File_Path
	def EasyREADME(self):
		EasyREAD = open('README.md', 'w')
		EasyREAD.writelines(self.README)
	def EasyInit(self):
		OldPath = os.getcwd()
		os.mkdir(self.Name)
		path = os.getcwd()
		os.chdir(path+'/'+self.Name)
		Init = open('__init__.py', 'w')
		with open(self.Main_File_Path) as f:
			InitText= f.readlines()
		Init.writelines(InitText)
		os.chdir(OldPath)
	def EasyLicense(self):
		LICENSE_TEXT = """MIT License

Copyright (c) 2019 """,self.Author,""" 

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (""",self.Name, """), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.""" 

		LICENSE = open('LICENSE', 'w')
		LICENSE.writelines(LICENSE_TEXT)
	def EasySetup(self):
		SETUP_TEXT = """import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="""+"'"+self.Name+"'"+""",
    version="""+"'"+self.Version+"'"+""",
    author="""+"'"+self.Author+"'"+""",
    author_email="""+"'"+self.Author_email+"'"+""",
    description="""+"'"+self.Project_Description+"'"+""",
    long_description="""+"'''"+self.README+"'''"+""",
    long_description_content_type="text/markdown",
    url="""+"'"+self.Homepage+"'"+""",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
"""
		setup = open('setup.py', 'w')
		setup.writelines(SETUP_TEXT)
	def EasyCreate(self):
		os.mkdir(self.Name)
		path = os.getcwd()
		os.chdir(path+'/'+self.Name)
		Package.EasySetup(self)
		Package.EasyLicense(self)
		Package.EasyInit(self)
		Package.EasyREADME(self)

