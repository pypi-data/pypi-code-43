from pianyuan import getInf
import os,sys
version = getInf.getVersion()
print(type(version))
upload_path = "twine upload " + os.getcwd()+"\\dist\\pianyuan-" + version + ".tar.gz"
def package():
    print("start packaging =================================")
    os.system(r"python setup.py sdist")
    print("start installing ================================")
    os.system(r"python setup.py install")

def upload():
   
    package()
    print("start upload=====================================")
    os.system(upload_path)
