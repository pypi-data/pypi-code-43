import fs
from fs.copy import copy_file
import pandas as pd
# todo remove on next release. bug.
import fs.osfs
import logging
log = logging.getLogger()

def save(self, obj):
    """ save pandas dataframe """
    # save locally
    if isinstance(self.ofs, fs.osfs.OSFS):
        self.ofs.makedirs(fs.path.dirname(self.path), recreate=True)
        obj.to_excel(self.path)
        return

    # save to temp file then upload
    local = fs.open_fs("")
    temp = f"temp/{self.path}"
    local.makedirs(fs.path.dirname(temp), recreate=True)
    obj.to_excel(temp)
    copy_file(local, temp, self.fs, self.path)

def load(self):
    """ load pandas dataframe """

    # read locally
    if isinstance(self.ofs, fs.osfs.OSFS):
        return pd.read_excel(self.path, index_col=0)

    # load from cache or download
    local = fs.open_fs("")
    temp = f"temp/{self.path}"
    if not local.exists(temp):
        local.makedirs(fs.path.dirname(temp), recreate=True)
        copy_file(self.fs, self.path, local, temp)
    return pd.read_excel(temp, index_col=0)