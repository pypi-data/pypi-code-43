# THIS FILE IS GENERATED FROM PADDLEPADDLE SETUP.PY
#
full_version    = '1.6.0'
major           = '1'
minor           = '6'
patch           = '0'
rc              = '0'
istaged         = False
commit          = '28f871d4bd9f239aefb2118bf3a83225630160af'
with_mkl        = 'ON'

def show():
    if istaged:
        print('full_version:', full_version)
        print('major:', major)
        print('minor:', minor)
        print('patch:', patch)
        print('rc:', rc)
    else:
        print('commit:', commit)

def mkl():
    return with_mkl
