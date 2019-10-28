import getpass
class acc:
    def __init__(self):
        temp = open('passw.txt', 'a')
        temp.close()
        self.contents = open('passw.txt', 'r').read()
        self.message = 'Here Are The Saved Passwords::\n'+self.contents+'\n'
    def __str__(self):
        return self.message
class usercreator:
    def __init__(self, username, passw):
        self.username = username
        self.passw = passw
    def saver(self):
        f = open('passw.txt', 'a')
        f.write('\n')
        f.write(str(self.username)+'    ')
        f.write(str(self.passw))
        f.close()
        f = open('passw.txt', 'r')
        for line in f:
            line = line.strip()
            info = line.split('    ')
        return info
def login(Username, passw, casesenseu=False, casesensp=True):
    if casesensp == True and casesenseu == True:
        accs = []
        cor = False
        for line in open('passw.txt', 'r'):
            line = line.strip()
            if line != '':
                accs = line.split('    ')
                acco = {accs[0]:accs[1]}
                acco2 = {accs[1]:accs[0]}
                if Username == accs[0] and passw == accs[1]:
                    return True
                else:
                    cor = False
        return cor
    elif casesensp == False and casesenseu == False:
        accs = []
        cor = False
        for line in open('passw.txt', 'r'):
            line = line.strip()
            if line != '':
                accs = line.split('    ')
                acco = {accs[0]:accs[1]}
                acco2 = {accs[1]:accs[0]}
                if Username.lower() == accs[0].lower() and passw.lower() == accs[1].lower():
                    return True
                else:
                    cor = False
        return cor
    elif casesenseu == True and casesensp == False:
        accs = []
        cor = False
        for line in open('passw.txt', 'r'):
            line = line.strip()
            if line != '':
                accs = line.split('    ')
                acco = {accs[0]:accs[1]}
                acco2 = {accs[1]:accs[0]}
                if Username == accs[0] and passw.lower() == accs[1].lower():
                    return True
                else:
                    cor = False
        return cor
    elif casesensp == True and casesenseu == False:
        accs = []
        cor = False
        for line in open('passw.txt', 'r'):
            line = line.strip()
            if line != '':
                accs = line.split('    ')
                acco = {accs[0]:accs[1]}
                acco2 = {accs[1]:accs[0]}
                if Username.lower() == accs[0].lower() and passw == accs[1]:
                    return True
                else:
                    cor = False
        return cor
def createacc(usrname, password):
    usr = usercreator(usrname, password)
    usr.saver()