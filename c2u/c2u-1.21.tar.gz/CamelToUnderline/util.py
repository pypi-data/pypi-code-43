def c2u(input):
    '''
    Example:
    >>> c2u.c2u("fTf")
    'f_tf'

    '''

    if type(input)=='list':
        return [c2u(i) for i in list]
    else:



        out=''
        for i in range(len(input)):
            if input[i].isupper():
                out+=('_')
                out+=input[i].lower()
            else:
                out+=input[i]


        return out

def u2c(input):

    '''
    Example
>>> c2u.u2c("dfa_dfsa")
'dfaDfsa'
    '''

    if type(input)=='list':
        return [u2c(i) for i in list]


    else:
        out=''
        for i in range(len(input)):
            if i>0 and input[i-1]=='_':
                continue
            if input[i]=='_':


                out+=input[i+1].upper()
            else:
                out+=input[i]
        return out
