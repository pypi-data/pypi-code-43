import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="sysapi",
    version="0.0.28",
    author="Olivier Dalle",
    author_email="olivier@safer-storage.com",
    description="A REST API service to query and manage the SAFER-STORAGE backup and storage in space in time dimensions",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.safer-storage.com/safer-dev-priv/nas-sysapi",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: European Union Public Licence 1.2 (EUPL 1.2)",
        "Operating System :: POSIX :: Linux",
    ],
    python_requires='>=3.7.3',
    install_requires=[
        'fastapi',
        'uvicorn',
        'email-validator',
        'pyzfs',
        'pickledbod',
        'setuptools',
        'twine',
        'wheel'
    ],
    include_package_data=True,
    data_files = [('.', ['config.json', 'params.json'])],
    scripts = ['bin/cleanup.sh', 'bin/preptest.sh']
)