'''
Created on Feb 1, 2018

@author: stelios
'''

import os

datahost= os.environ.get('datahost', '')
datadata=os.environ.get('datadata', 'ATLASDR1')
datauser=os.environ.get('datauser', '')
datapass=os.environ.get('datapass', '')
adminuser=os.environ.get('adminuser', '')
adminpass=os.environ.get('adminpass', '')
admingroup=os.environ.get('admingroup', '')
datacatalog=os.environ.get('datacatalog', 'ATLASDR1')
datatype=os.environ.get('datatype', 'mssql')
datadriver="net.sourceforge.jtds.jdbc.Driver"
dataurl=os.environ.get('dataurl', '')
endpoint=os.environ.get('endpoint', '')
osa_endpoint= os.environ.get('osa_endpoint', '')
maxrows= os.environ.get('maxrows', 1000000)
