# MousikóFídi
# Copyright (C) 2019  Hristos N. Triantafillou
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
import shutil
import subprocess


from datetime import datetime
from setuptools import setup


with open("README.md", "r") as r:
    long_desc = r.read()

with open("requirements.txt", "r") as f:
    _req = f.readlines()

req = []
for r in _req:
    req.append(r.strip("\n"))

git = shutil.which("git")

if git:
    exact_tag = subprocess.run(
        ["git", "describe", "--exact-match", "--tags", "HEAD"],
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE,
    )

    err = exact_tag.stderr.decode()
    if not err:
        ver = exact_tag.stdout.decode().strip("\n")

    not_tag = subprocess.run(
        ["git", "describe", "--tags"], stderr=subprocess.PIPE, stdout=subprocess.PIPE
    )

    err2 = not_tag.stderr.decode()
    if not err2:
        ver = not_tag.stdout.decode().strip("\n")

    lc = subprocess.run(
        "git diff-index --quiet HEAD".split(" "),
        stderr=subprocess.PIPE,
        stdout=subprocess.PIPE,
    )

    local_changes = lc.returncode == 1
    if local_changes:
        ver = ver + "-devel"

else:
    fmt = "%Y%m%d%H%M%S"
    now = datetime.now()
    ver = now.strftime(fmt)


setup(
    name="MousikoFidi",
    version=ver,
    author="Hristos N. Triantafillou",
    author_email="me@hristos.co",
    description="MousikoFidi: Your Music Cloud",
    long_description=long_desc,
    long_description_content_type="text/markdown",
    url="https://git.sr.ht/~hristoast/mousikofidi",
    packages=["mousikofidi"],
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Web Environment",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "License :: OSI Approved",
        "Natural Language :: English",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: JavaScript",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: Internet :: WWW/HTTP",
        "Topic :: Internet :: WWW/HTTP :: Browsers",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content :: Content Management System",
        "Topic :: Multimedia",
        "Topic :: Multimedia :: Sound/Audio",
        "Topic :: Multimedia :: Sound/Audio :: Mixers",
        "Topic :: Multimedia :: Sound/Audio :: Players",
        "Topic :: Multimedia :: Sound/Audio :: Players :: MP3",
        "Topic :: Multimedia :: Video",
        "Topic :: Multimedia :: Video :: Display",
    ],
    install_requires=req,
    python_requires=">=3.5",
    scripts=["example/mousikofidi", "example/mousikofidi-client"],
)
