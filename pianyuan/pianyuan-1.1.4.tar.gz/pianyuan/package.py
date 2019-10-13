from pianyuan import getInf
import os,sys
version = getInf.getVersion()
upload_path = "twine upload " + os.getcwd()+"\\dist\\pianyuan-" + version + ".tar.gz"
def package():
    print("start packaging =================================")
    os.system(r"python setup.py sdist")

def upload():
    package()
    print("start upload=====================================")
    os.system(upload_path)
    os.system(r"pip uninstall pianyuan")
    os.system(r"pip install  pianyuan")
