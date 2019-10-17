import pandas as pd
import subprocess
import os
from . import api 

RELEASE_FILE = "releases.csv"

if not os.path.exists(RELEASE_FILE):
  print("Recreating releases")
  releases = pd.DataFrame({"name": [], "id": [], "hash": [], "isActive": []})
  releases.to_csv(path_or_buf=RELEASE_FILE)



def list():
  releases = pd.read_csv(RELEASE_FILE).drop("Unnamed: 0", axis=1)
  return releases

def create(release_name, release_id, model_type, is_active=False):
  releases = list()
  git_hash = subprocess.check_output(['git', 'rev-parse', 'HEAD']).strip()
  new_release = ({"name": release_name, "id": release_id, "hash": git_hash, "isActive": is_active, "modelType": model_type})
  releases = releases.append(new_release, ignore_index=True)
  print(releases)
  releases.to_csv(path_or_buf=RELEASE_FILE)
  return releases

def deploy(release_id):
  releases = list()
  releases.loc[releases["id"] == release_id, "isActive"] = True
  releases.to_csv(path_or_buf=RELEASE_FILE)
  return releases

def disable(release_id):
  releases = list()
  releases.loc[releases["id"] == release_id, "isActive"] = False
  releases.to_csv(path_or_buf=RELEASE_FILE)
  return releases