import numpy as np
import math
import string, random


# VERSION
version="0.1.3"

BLANKCODE=99
# 알파벳만 추출한다.
def alphaonly(line):
    retline=[]
    for a in line:
        if a.isalpha():
            retline.append(a)
    return retline

def altocode(line):
    retline=[]
    for a in line:
        if a.isalpha():
            if a.isupper():
                retline.append(ord(a)-ord('A'))
            else:
                retline.append(ord(a)-ord('a'))
        else:
            retline.append(BLANKCODE) # no alphabet.
    return retline

# inverse factor of * mod 26 operator.
# key * i === 1 (mod 26)
def inversefactor(key):
    for i in range(26):
        if (key*i)%26==1:
            return i
    return -1 # not found


# 리스트 성분을 길이에 맞춰 출력.
# 일정한 길이로 필드를 출력함.
# alonly: 스트링 타입인데 알파벳이 아닌 부분은 출력 안 함.
def printlist(head, al, itemlength, alonly=True):
    strlist = []
    for a in al:
        if alonly:
            if type(a)==str and (not a.isalpha()) :
                continue
        strlist.append(("{:>"+str(itemlength)+"}").format(a))
    print(head, ''.join(strlist), sep='')


def jake_encrypt(keys, plain):
#     plain=plain.upper()   ## upper case only!!!
    if len(keys)%2==0 or len(keys)<3:
        return ''
    apinkeys=[]
    evencnt=int(len(keys)/2)
    for i in range(evencnt):
        apinkeys.append((keys[i*2], keys[i*2+1]))
    ulkey = keys[-1]

    # key valid check
    for a,b in apinkeys:
        if a%2==0:
            return ''
        if a%13==0:
            return ''

    keypair=len(apinkeys)
    i=0
    midcipher=""
    plaincode=[]
    calc1=[]
    calc2=[]
    for c in plain:
        uppercase = c.isupper()
        if c.isalpha():
            if uppercase:
                code = ord(c)-ord('A')
            else:
                code = ord(c)-ord('a')
            plaincode.append(code)
            a = apinkeys[i%keypair][0]
            b = apinkeys[i%keypair][1]
            vv = code*a+b
            calc1.append(vv)
            enc = (vv)%26
            calc2.append(enc)
            if uppercase:
                encchar = chr(enc+ord('A'))
            else:
                encchar = chr(enc+ord('a'))
            midcipher+=encchar
            i+=1
        else:
            midcipher+=c

    blocksize = math.ceil(len(midcipher)/ulkey)*ulkey
    midcipher2 = midcipher+' '*(blocksize-len(midcipher))

    rows = ulkey
    cols = int(blocksize/ulkey)
    mat = np.asarray(list(midcipher2))
    mat = mat.reshape((rows, cols))

    matt = mat.T
    matlist = list(matt.reshape(-1))
    lastcipher = ''.join(matlist)

    return lastcipher

'''
keys : key
lastcipher : ciphertext
padremove : True/Flase : space padding remove
'''
def jake_decrypt(keys, lastcipher, padremove=True):
    if len(keys)%2==0 or len(keys)<3:
        return ''
    apinkeys=[]
    evencnt=int(len(keys)/2)
    for i in range(evencnt):
        apinkeys.append((keys[i*2], keys[i*2+1]))
    ulkey = keys[-1]

    # dec ultari
    blocksize = math.ceil(len(lastcipher)/ulkey)*ulkey
    lastcipher2 = lastcipher+' '*(blocksize-len(lastcipher))
    keypair=len(apinkeys)

    rows = ulkey
    cols = int(blocksize/ulkey)

    mat = np.asarray(list(lastcipher2))

    mat = mat.reshape((cols, rows))
    matt = mat.T

    matlist = list(matt.reshape(-1))
    middec = ''.join(matlist)

    ### 아핀 암호 복호화

    i=0
    lastdec=""
    midcode=[]
    calc2=[]
    for c in middec:
        uppercase = c.isupper()
        if c.isalpha():
            if uppercase:
                code = ord(c)-ord('A')
            else:
                code = ord(c)-ord('a')
            midcode.append(code)
            a = apinkeys[i%keypair][0]
            b = apinkeys[i%keypair][1]
            alpha = 0
            while (alpha+code-b)%a!=0:
                alpha += 26
            dec = int ( ((alpha+code-b)/a)%26 )
            calc2.append(dec)
            if uppercase:
                decchar = chr(dec+ord('A'))
            else:
                decchar = chr(dec+ord('a'))
            lastdec+=decchar
            i+=1
        else:
            lastdec+=c

    if padremove:
        lastdec = lastdec.rstrip(' ')
    return lastdec


def make_random_string(nlen):
    return ''.join(random.choice(string.printable) for i in range(nlen))


# 패스워드로 키값을 생성한다.
# 울티리키는 최소 2부터 생성됨.
def make_jake_key(passphase):
    keys=[]
    if len(passphase)==0:
        return None
    if len(passphase)==1:
        passphase+=passphase
    for c in passphase:
        if c.isupper():
            val = ord(c)-ord('A')+26
        elif c.islower():
            val = ord(c)-ord('a')
        else:
            val = ord(c)
        while True:
            if val%2==0 or val%13==0:
                val+=1
                continue
            break
        keys.append(val)
    if len(keys)%2==0:
        # append ulkey
        keys.append(keys[-1])
    keys[-1]=keys[-1]%8
    keys[-1]+=2
    return keys


