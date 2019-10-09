import locale
import os

class jdTranslationHelper():
    def __init__(self,lang=None,defaultLanguage="en_GB"):
        self.selectedLanguage = lang or locale.getlocale()[0]
        self.defaultLanguage = defaultLanguage
        self.strings = {}

    def readLanguageFile(self,path):
        with open(path,"r",encoding="utf-8") as f:
            lines = f.read().splitlines()
            for line in lines:
                try:
                    key, value = line.split("=",1)
                    self.strings[key] = value
                except:
                    print("Error loading line \"" + line + "\" in file " + path)

    def loadDirectory(self,path):
        if not os.path.isdir(os.path.join(path,self.defaultLanguage + ".lang")):
            print(path + " was not found")
            return
        self.readLanguageFile(os.path.join(path,self.defaultLanguage + ".lang"))
        if os.path.isfile(os.path.join(path,self.selectedLanguage + ".lang")):
            self.readLanguageFile(os.path.join(path,self.selectedLanguage + ".lang"))

    def translate(self,key,default=None):
        if key in self.strings:
            return self.strings[key]
        else:
            if default:
                return default
            else:
                return key
