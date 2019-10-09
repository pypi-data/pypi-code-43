"""
Repo operation example
"""
import os
import sys

sys.path.append("./../")

from mcutk.repo import Repo

# create instance from path
repo = Repo.frompath("C:/mcu-sdk-2.0")
print repo.repo_url
print repo.is_ready
print repo.get_branch_name()
print repo.get_latest_commit_message()
print repo.get_submodules()

repo.checkout_branch("master")
repo.AutoSync("master")


# create repo instance by url
repo = Repo("ssh://git@bitbucket.sw.nxp.com/mcucore/mcu-sdk-2.0.git")
print repo.repo_url
print repo.is_ready
print repo.get_branch_name()
print repo.get_latest_commit_message()
print repo.get_submodules()

repo.Clone(".", "master")
repo.AutoSync(".", "develop")

