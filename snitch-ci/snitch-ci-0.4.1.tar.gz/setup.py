import setuptools

import snitch

with open("README.md", "r") as fh:
    long_description = fh.read()

with open("requirements.txt", "r") as fh:
    install_requires = [line.strip() for line in fh]

setuptools.setup(
    name="snitch-ci",
    version=snitch.__version__,
    author=snitch.__author__,
    author_email="gregory@millasseau.fr",
    description="An input event recorder and player for automatic testing",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/irsn/snitch-ci",
    packages=setuptools.find_packages(),
    install_requires=install_requires,
    classifiers=[
        "Development Status :: 4 - Beta",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Natural Language :: English",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Topic :: Software Development :: Testing"
    ],
    entry_points={
        'console_scripts': [
            'snitch = snitch.__main__:main',
            'snitch-dump-images = snitch.tools.dump_images:main'
        ]
    }
)
