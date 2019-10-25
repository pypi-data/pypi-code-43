import io
import os

import setuptools

name = "admobilize-malos"
description = "AdMobilize Malos Library"
version = "0.0.1"

# Should be one of:
# 'Development Status :: 3 - Alpha'
# 'Development Status :: 4 - Beta'
# 'Development Status :: 5 - Production/Stable'
release_status = "Development Status :: 3 - Alpha"
dependencies = [
    'docopt>=0.6.2',
    'admobilizeapis>=0.0.32',
    'pyzmq>=18.0.1'
]
extras = {}

# Boilerplate below this line
package_root = os.path.abspath(os.path.dirname(__file__))
readme_filename = os.path.join(package_root, "README.rst")
with io.open(readme_filename, encoding="utf-8") as readme_file:
    readme = readme_file.read()

# Only include packages under the 'admobilize' namespace. Do not include tests,
# benchmarks, etc.
packages = [
    package
    for package in setuptools.find_packages()
    if package.startswith("admobilize")
]

namespaces = ["admobilize"]

setuptools.setup(
    name=name,
    version=version,
    description=description,
    long_description=readme,
    author="AdMobilize Team",
    author_email="devel@admobilize.com",
    url="https://bitbucket.com/admobilize/malos-python",
    license='GPLv3',
    classifiers=[
        release_status,
        "Intended Audience :: Developers",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
    ],
    platforms="Posix; MacOS X; Windows",
    packages=packages,
    namespace_packages=namespaces,
    install_requires=dependencies,
    entry_points={
        'console_scripts': [
            'malosclient=admobilize.malos.cli:main',
        ],
    },
    extras_require=extras,
    python_requires=">=3.6.*",
    zip_safe=False,
)
