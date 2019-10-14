import time
import imp

a = imp.load_source('', '/home/jkotan/ndts/nexdatas.selector/nxselector')
nxselector = a.main()
time.sleep(20)
