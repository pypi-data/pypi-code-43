import numpy as np
import pact.pdb as pdb
import h5py

fp = pdb.open("junk.pfb","r")
hf = h5py.File("junk.h5","w")

din = np.array(fp.read('x@global'))
din2 = din
din = din.reshape(din.shape[::-1]).transpose()
fp.close()

hf.create_dataset('x@global',data=din)
hf.close()
hf = h5py.File("junk.h5","r")
hin = np.array(hf.get("x@global"))

fp = pdb.open("junk2.pfb","w")
fp.write("x@global",hin.transpose().reshape(hin.shape).tolist())
fp.close()

