
import sys,os
import glob
from distutils.spawn import find_executable


print "do level 2 tests of python version"


h5diff = find_executable('h5diff')
if h5diff == None:
    print 'No h5diff found in your PATH.'
    sys.exit(1)
   
tests = glob.glob('*.py')
try:
    os.mkdir('pyres')
except:
    pass
os.chdir('pyres')


results = {}
oorig = sys.stdout
eorig = sys.stderr
for tf in tests:
    if tf != 'dotest.py':
        t = os.path.splitext(tf)[0]
        try:
           with open(t+".res","wb") as f:
              sys.stdout = f
              sys.stderr = f
              execfile('../'+tf)
              f.close()
              results.update({tf:'   Passed'})
        except:
           results.update({tf:'***Failed'})
    sys.stdout = oorig
    sys.stderr = eorig

print
print
print '------------------------'
for k in results.keys():
   print  k,results[k]
  
