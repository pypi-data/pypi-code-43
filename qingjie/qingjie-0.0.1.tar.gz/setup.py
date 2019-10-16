import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()


setuptools.setup(
        name="qingjie",
        version="0.0.1",
        author="cookiery",
        author_email="2061803022@qq.com",
        description="test",
        long_description=long_description,
        license="MIT",
        url="https://pypi.org/manage/projects",
        packages=setuptools.find_packages(),
        classifiers=[
            "Programming Language :: Python",
            "License :: OSI Approved :: MIT License",
            "Operating System :: OS Independent",
            ]
        )
