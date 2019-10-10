import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="cau_utilities",
    version="0.0.4",
    author="Cauã S. C. P.",
    author_email="cauascp37@gmail.com",
    description="this project has a lot of utilities made by Caua_SCP.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://www.youtube.com/channel/UCAbwAklWIeuoKKjVBMQVCew",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6'
    ,
    install_requires=[
        'importFromParent',
    ]
    ,
    zip_safe=False
)
