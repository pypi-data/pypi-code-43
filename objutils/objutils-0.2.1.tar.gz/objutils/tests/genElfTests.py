
from collections import defaultdict
import json
import os
import subprocess

"""
flist = file("flist.txt").readlines()

print(__file__)

#results = defaultdict()
results = {}

pth = os.path.abspath('./ELFFiles')
#for fname in os.listdir(pth):
for fname in flist:
  fname = fname.strip()
  #fname = fname.split("/")[1]
#  fname, _ = fname.split("/")
#  afn = os.path.join(pth, fname)
  afn = os.path.join("./ELFFiles", fname)

#  print(afn)
 # print("*** {:^80} ***".format(afn))

  res = subprocess.Popen('readelf -h "{}" 2>&1'.format(afn), stdout = subprocess.PIPE, shell = True)
  result = res.communicate()[0]
  results[fname] = result

print(json.dumps(results))
"""

