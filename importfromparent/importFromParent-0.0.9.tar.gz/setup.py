import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

version_ = []

with open("version_start.txt", "r") as start:
    version_.append(start.read())

with open("version_end.txt", "r") as end:
    end_ = int(str(end.read()))
    end_ = str(end_ + 1)
    open("version_end.txt", "w").write(end_)
with open("version_end.txt", "r") as end:
    version_.append(end.read())

with open("package_name.txt", "r") as file_:
    package_name = file_.read()
    
version_ = ''.join(version_)
#print(version_)

with open("pipInstall.bat", "w+") as file:
    file.write(f"pip uninstall {package_name}\npip install {package_name}=={version_}")

setuptools.setup(
    name=package_name,
    version=version_,
    author="Cauã S. C. P.",
    author_email="cauascp37@gmail.com",
    description="import a package or a module from a py file's parent.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://www.youtube.com/channel/UCAbwAklWIeuoKKjVBMQVCew",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)
