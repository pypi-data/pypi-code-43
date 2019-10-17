import os
from setuptools import setup

dir_path = os.path.dirname(os.path.abspath(__file__))

description = """Blurryface"""
package_name = "blurryface"
requirements = open(os.path.join(dir_path, "requirements.txt")).read()
version = open(os.path.join(dir_path, "VERSION")).read().strip()

def package_files():
    paths = []
    for (path, directories, filenames) in os.walk(package_name):
        for filename in filenames:
            paths.append(os.path.join('..', path, filename))
    return paths

setup(
    name=package_name,
    version=version,
    description=description,
    install_requires=requirements,
    packages=[package_name],
    package_data={'': package_files()},
    entry_points={
        "console_scripts": [
            "blurryface = blurryface:print_help",
            "blurryface-video = blurryface.blurryface_video:main",
            "blurryface-image = blurryface.blurryface_image:main"
        ]
    },
    author="Jason Darnell",
    email="jason.darnell@daugherty.com",
    license="Proprietary",
    url=""
)
