
memory = """
import uos
import json

s = uos.statvfs('.')
data = {{'total': (s[1]*s[2]), 'unused': (s[1]*s[3]), 'unused_p': 100*(s[1]*s[3])/(s[1]*s[2])}}
print(json.dumps({{'response':data, 'snippet':'memory'}}))
"""

walk = """
import uos
import sys
import json

def walk(root = '/'):
    ''''''
    dirs = []
    files = []

    for p in uos.listdir(root):

        t_root = '{{}}/{{}}'.format(root.strip('/'), p.strip('/'))
        try:
            uos.listdir(t_root)
            dirs.append(p)
            for a in walk(t_root):
                yield a
        except:
            #files.append(p)
            if p.endswith('__espresso__.py'):

                p_orig = p[:p.find('___')] + '.py'
                t_root_orig = t_root.replace(p, p_orig)

                if p_orig in uos.listdir(root):
                    uos.remove(t_root)
                else:
                    uos.rename(t_root, t_root_orig)


                files.append(p_orig)

            else:
                files.append(p)

    yield root, dirs, files

data = []
for root, dirs, files in walk('/'):
    root = root.strip('/')
    root = '/'+root

    if root == '/':
        level = 0
    else:
        level = root.count('/')

    for f in files:
        data.append((level+1, f, root+'/'+f))
    data.append((level, root, None))

data.reverse()

s = uos.statvfs('.')
data_m = {{'total': (s[1]*s[2]), 'unused': (s[1]*s[3]), 'unused_p': 100*(s[1]*s[3])/(s[1]*s[2])}}

print(json.dumps([{{'response':data, 'snippet':'walk'}}, {{'response':data_m, 'snippet':'memory'}},]))
"""


readfile = """
import json

with open('{0}', 'r') as file:
    content = file.read()
    print(json.dumps({{'response':content, 'path':'{0}', 'snippet':'readfile'}}))
    """

readchunk = """
espresso.read_chunk('{0}', {1})
"""

# readchunk = """
# import json

# with open('{0}', 'r') as file:
    # content = file.read()
    # print(json.dumps({{'response':content, 'path':'{0}', 'snippet':'readchunk'}}))
    # """

writefile = """
with open('{0}', 'w') as file:
    file.write('''{1}''')
"""

# writechunck = """
# import json

# with open('{0}', 'a') as file:
    # file.write('''{1}''')
    # print(json.dumps({{'response':True, 'path':'{0}', 'snippet':'writefile'}}))
# """

runfile = """
import uos

uos.chdir('{0}')
uos.rename('{1}.py', '{2}.py')
try:
    import {2}
except Exception as e:
    print(e)
finally:
    uos.rename('{2}.py', '{1}.py')
"""


newfile = """
file = open('{0}', 'w')
file.close()
""" + walk

newfolder = """
import uos
uos.mkdir('{0}')
""" + walk

rename = """
import uos
uos.rename('{0}', '{1}')

if {2}:
    with open('{1}', 'r') as file:
        content = file.read()
        open_ = {{'response': content, 'path': '{1}', 'snippet': 'readfile'}}
else:
    open_ = {{}}

""" + '\n'.join(walk.split('\n')[:-2]) + """
print(json.dumps([open_,
                  {{'response':data, 'snippet':'walk'}},
                  {{'response':data_m, 'snippet':'memory'}},
                  ]))
"""

rename_nowalk = """
import uos
uos.rename('{0}', '{1}')

if {2}:
    with open('{1}', 'r') as file:
        content = file.read()
        open_ = {{'response': content, 'path': '{1}', 'snippet': 'readfile'}}
else:
    open_ = {{}}

"""


reboot = """
import machine
machine.reset()
""" + walk


removefile = """
import uos
uos.remove('{0}')
"""

# removefile_nowalk = """
# import uos
# uos.remove('{0}')
# """


removefolder = """
import uos
import sys

def removefolder(root = '/'):
    ''''''
    dirs = []
    files = []

    for p in uos.listdir(root):

        t_root = '{{}}/{{}}'.format(root.strip('/'), p.strip('/'))
        try:
            uos.listdir(t_root)
            dirs.append(p)
            for a in removefolder(t_root):
                yield a
        except:
            files.append(p)

    yield root, dirs, files

for root, dirs, files in removefolder('{0}'):
    for file in files:
        uos.remove(root + '/' + file)
    uos.rmdir(root)
""" + walk


listlibs = """
import uos
import ujson

try:
    libs = uos.listdir('/lib')
except:
    libs = []
print(ujson.dumps({{'response':libs, 'snippet':'listlibs'}}))
"""

# reload = """
# import usys
# del usys.modules['{0}']
# import {0}
# """

install = """
import upip
upip.install('{0}')
""" + walk
