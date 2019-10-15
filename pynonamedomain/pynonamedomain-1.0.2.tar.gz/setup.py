from setuptools import setup, find_packages

def readme():
    return open("README.md", "r").read()

setup(
    name = "pynonamedomain",
    version = "1.0.2",
    description = "Unofficial NonameDomain API module/client",
    long_description = readme(),
    long_description_content_type = "text/markdown",
    url = "https://gitlab.com/slacker/pynonamedomain",
    packages = find_packages(),
    include_package_data = True,
    install_requires = [
        "Click",
        "requests",
        "tldextract",
    ],
    entry_points = {
        "console_scripts": [
        "nnd-cli = pynonamedomain.nnd_cli:cli",
        ]
    },
    classifiers = {
        "Development Status :: 5 - Production/Stable",
        "Environment :: Console",
        "Intended Audience :: Developers",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Internet :: Name Service (DNS)",
        "Topic :: Software Development :: Libraries",
        "Topic :: Utilities"
    },
    keywords = "nonamedomain nonamedomain.hu dns",
    license = "GPLv3+",
)
