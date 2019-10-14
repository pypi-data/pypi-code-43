import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="screen_search",
    version="1.0",
    author="alimiracle",
    author_email="alimiracle@riseup.net",
    description="A small python library use to  Searchs for an image on the screen",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://notabug.org/alimiracle/screen_search",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python",
        "License :: OSI Approved :: GNU Affero General Public License v3",
        "Operating System :: OS Independent",
    ],
    install_requires=[
   'opencv-python',
   'pyobjc-core;platform_system=="Darwin"', 
   'pyobjc;platform_system=="Darwin"',
   'python3-Xlib;platform_system=="Linux" and python_version>="3.0"',
   'Xlib;platform_system=="Linux" and python_version<"3.0"',
   'pyautogui',
   'numpy'
],
)
