import setuptools

setuptools.setup(
    name="pairfinder",
    version="1.0.3",
    license='MIT',
    author="parallel",
    author_email="parallel9973@gmail.com",
    description="Finder for pairs trading",
    long_description=open('README.md').read(),
    url="https://github.com/parallel/pairfinder",
    packages=setuptools.find_packages(),
    classifiers=[
        # 패키지에 대한 태그
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
)