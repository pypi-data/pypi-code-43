import os
from datetime import datetime
now = str(datetime.now())
year = now[:4]
cwd = os.getcwd()
print("Open File Explorer On Windows Or Finder On Mac And Go To", cwd, "Because This Is Where We Will Be Working!!\n")
name1 = input('What Would You Like folder name to be?\n')
os.mkdir(name1)
print("In this folder there will be another folder which you will import from and also will be what people will pip install")
fro = input("what would you like that folder to be?\n")
os.chdir(name1)
os.mkdir(fro)
minpython = input("What is the minimum python version for your program?\n")
author = input("Author Name?\n")
authoremail = input("Author email?\n")
shortdesc = input("Short Description?   All that info can be later modified in the setup.py\n")
user = input("What Should Your Name Be Written As In The Lisence/Copyright\n")
requirements = input('What are the non-default modules that are required---seperate by comas and put in between "" for eg. "termcolor", "afroy"\n')
lisence = open("LISENCE", "a")
lisence.close()
lisence = open("LISENCE", 'w')
lisence.write('''MIT License

Copyright (c) ''' + year + ''' ''' + user + '''

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
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
SOFTWARE.''')
lisence.close()
manifest = open('MANIFEST.in', 'a')
manifest.close()
manifest = open('MANIFEST.in', 'w')
manifest.write("include LISENCE README.md ")
manifest.close()
setup = open('setup.py', 'a')
setup.close()
setup = open('setup.py', 'w')
setup.write('''import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="''' + fro + '''",####the same name as the name in the __init__.py
    version="0.0.0",
    author="'''+author+'''",
    author_email="'''+authoremail+'''",
    description="'''+shortdesc+'''",
    long_description=long_description,####Change Everything except this and the line under
    long_description_content_type="text/markdown",
    url="",
    install_requires=['''+requirements+'''],###non default modules that you import in your code seperated by comas and in between ""
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>='''+minpython+'''',
)''')
setup.close()
readme = open('README.md', 'a')
readme.close()
input("Edit The readme.md as this will be the description of your pip on the website once you finish    [Press Enter To Continue]")
os.chdir(fro)
init = open("__init__.py", 'a')
init.close()
init = open("__init__.py", 'w')
init.write('name = "'+fro+'"')
init.close()
f = input("People will import this what should it be called?\n")
file = open(f+".py", 'a')
file.close()
print('You Must Have A Pypi.org Account')
input("Edit the " + f +'.py to the code you want to publish    [Press Enter To Continue]')
input("Click Enter To Begin Publish Program    Make sure you have all files ready")
os.chdir(cwd)
os.chdir(name1)
try:
    os.system('python setup.py sdist && twine upload dist\*')
except:
    os.system('python setup.py sdist && twine upload dist/*')
input("[Press Enter To Quit The Program]")