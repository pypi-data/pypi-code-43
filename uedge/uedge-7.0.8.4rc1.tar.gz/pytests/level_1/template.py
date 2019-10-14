#Coarse mesh [com.nx=8, com.ny=4] for DIII-D MHD equilibrium
#Uses diffusive neutrals, so five variables [bbb.ni,bbb.upi,Te,Ti,bbb.ng]
#
import sys,os

sys.path.insert(0,os.getcwd()+'/../../../pyscripts')
sys.path.insert(0,os.getcwd()+'/../../..')
from uedge import *

failed = False

if failed: raise Exception('data error')
