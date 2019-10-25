import setuptools

setuptools.setup(
    name="python-deploy",
    version="1.2",
    author="msm",
    author_email="msm@cert.pl",
    description="deploy",
    package_dir={"deploy": "src"},
    url="https://vcs.cert.pl/cert/deploy",
    packages=["deploy"],
    scripts=["src/deploy"],
    include_package_data=True,
    zip_safe=False,
    install_requires=[],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
)
