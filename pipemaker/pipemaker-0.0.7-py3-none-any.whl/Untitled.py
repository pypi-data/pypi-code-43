# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.2'
#       jupytext_version: 1.2.1
#   kernelspec:
#     display_name: Python 3
#     language: python
#     name: python3
# ---

# %%
import os
import subprocess
ignorefolders = ["nbs", "docs", "models", "data", "env", "venv"]
gitfiles = subprocess.run(["git", "ls-files"], check=True, capture_output=True, text=True).stdout.splitlines()
gitfolders = [d[:d.rfind("/")] for d in gitfiles if d.find("/") >= 0]
allfolders = [d[0].replace(os.path.sep, "/")[2:] for d in os.walk(".")]
excluded = list(set(allfolders) - set(gitfolders))
excluded = excluded + ignorefolders
#excluded.remove("")

# %%
sorted(excluded)

# %%
