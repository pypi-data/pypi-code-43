import pyking.docs.matext as matext


def creat_mat_doc():
    with open('matdoc.md', 'wt', encoding='utf-8') as f:
        f.write(matext.text1)
    return
