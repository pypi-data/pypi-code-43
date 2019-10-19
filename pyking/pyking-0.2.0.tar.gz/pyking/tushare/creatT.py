import pyking.docs.tutext as tut


def creat_py_doc():
    with open('tuJson.py', 'wt', encoding='utf-8') as f:
        f.write(tut.text1)
    with open('tuSdk.py', 'wt', encoding='utf-8') as f:
        f.write(tut.text2)
    return


def creat_api_doc():
    with open('document.json', 'wt', encoding='utf-8') as f:
        f.write()
