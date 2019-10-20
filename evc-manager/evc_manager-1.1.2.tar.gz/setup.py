import setuptools
import yaml

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="evc_manager",
    version="1.1.2",
    author="AmLight Dev Team",
    author_email="dev@amlight.net",
    description="A tool to create Ethernet Virtual Circuit in SDN environments",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/amlight/evc_manager",
    packages=setuptools.find_packages(),
    install_requires=[line.strip()
                      for line in open("evc_manager/requirements.txt").readlines()
                      if not line.startswith('#')],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        'Operating System :: POSIX :: Linux',
        'Topic :: System :: Networking',
        'Environment :: Console',
        'Environment :: No Input/Output (Daemon)',
    ],
    python_requires='>=3.6',
)
