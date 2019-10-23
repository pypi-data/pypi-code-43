import struct
import elist.elist as elel
import re
import copy
import pty
import os


#LE           Little- Endian
#BE           Big-Endian
#OOB          Out-Of-Band

#chbyts      char-bytes
#bytstrm     bytes-stream
#rm          remove

#BOM 是整个字节流有一个，而不是每个char-bytes
#不带le ,be 的encode keywords,既可以处理 带LE-BOM的(LE 的) 也能处理不带BOM的
#BOM 可以用来标明字节顺序 LE or BE
#utf-8 不需要
#这样如果接收者收到 FEFF，就表明这个字节流是 Big-Endian 的；
#如果收到FFFE 就表明这个字节流是 Little- Endian 的
# '你'.encode('utf_16')
# b'\xff\xfe`O'
# 表明utf_16的编码默认是 LE
# b'`O' == b'\x60\x4f'
# 那么 就是说4f在前60在后
# >>> '\u4f60'
# '你'
# >>>
# '你'.encode('utf_16_le')  是不带BOM的
# b'`O'
# '你'.encode('utf_16_be')  是不带BOM的
# b'O`' == b'\x4f\x60'
# 使用\u显示时 都是BE 序列 

def get_bominfo(bs,**kwargs):
    '''
        #only support utf-16 utf-32
        #LE           Little- Endian
        #BE           Big-Endian
        #OOB          Out-Of-Band (withour BOM)
        
        bs = b'\xff\xfe\x60\x4f'
        get_bominfo(bs)
        bs = b'\x60\x4f'
        get_bominfo(bs)
        bs = b'\xfe\xff\x4f\x60'
        get_bominfo(bs)
        bs = b'\x4f\x60'
        get_bominfo(bs)
        bs = b'\xff\xfe\x00\x00\x60\x4f\x00\x00'
        get_bominfo(bs)
        bs = b'\x60\x4f\x00\x00'
        get_bominfo(bs)
        bs = b'\x00\x00\xfe\xff\x00\x00\x4f\x60'
        get_bominfo(bs)
        bs = b'\x00\x00\x4f\x60'
        get_bominfo(bs)
        
    '''
    bom = bs[:4]
    if(bom == b'\xff\xfe\x00\x00'):
        b = bs[4:]
        t = 'LE'
    elif(bom == b'\x00\x00\xfe\xff'):
        b = bs[4:]
        t = 'BE'
    else:
        bom = bs[:2]
        if(bom == b'\xff\xfe'):
            b = bs[2:]
            t = 'LE'
        elif(bom == b'\xfe\xff'):
            b = bs[2:]
            t = 'BE'
        else:
            b = bs
            t = 'OOB'
    return((b,t))

def remove_bom(bs,**kwargs):
    '''
        #only support utf-16 utf-32 
        
        #LE           Little- Endian
        #BE           Big-Endian
        #OOB          Out-Of-Band (withour BOM)
        
        bs = b'\xff\xfe\x60\x4f'
        remove_bom(bs)
        bs = b'\x60\x4f'
        remove_bom(bs)
        bs = b'\xfe\xff\x4f\x60'
        remove_bom(bs)
        bs = b'\x4f\x60'
        remove_bom(bs)
        bs = b'\xff\xfe\x00\x00\x60\x4f\x00\x00'
        remove_bom(bs)
        bs = b'\x60\x4f\x00\x00'
        remove_bom(bs)
        bs = b'\x00\x00\xfe\xff\x00\x00\x4f\x60'
        remove_bom(bs)
        bs = b'\x00\x00\x4f\x60'
        remove_bom(bs)
    '''
    bominfo = get_bominfo(bs,**kwargs)
    return(bominfo[0])


#decode_chbyts         decode-char-bytes (to char)
#byts2chstr            decode-char-bytes (to char)
#unpack_chbyts         decode-char-bytes (to char)

def decode_chbyts(bs,**kwargs):
    '''
        #only support utf-8 utf-16 utf-32 
        
        
        #LE           Little- Endian
        #BE           Big-Endian
        #OOB          Out-Of-Band (withour BOM)
        
        bs = b'\x4f\x60'
        decode_chbyts(bs)
        bs = b'\x4f\x60'
        decode_chbyts(bs,style='js')
        bs = b'\\u4f60'
        decode_chbyts(bs,style='py')
        bs = b'\xff\xfe\x60\x4f'
        decode_chbyts(bs,encode = 'utf_16')
        bs = b'\x60\x4f'
        decode_chbyts(bs,encode = 'utf_16_le')
        bs = b'\xfe\xff\x4f\x60'
        decode_chbyts(bs,encode = 'utf_16_be')
        bs = b'\x4f\x60'
        decode_chbyts(bs,encode = 'utf_16_be')
        bs = b'\xff\xfe\x00\x00\x60\x4f\x00\x00'
        decode_chbyts(bs,encode = 'utf_32')
        bs = b'\x60\x4f\x00\x00'
        decode_chbyts(bs,encode = 'utf_32_le')
        bs = b'\x00\x00\xfe\xff\x00\x00\x4f\x60'
        decode_chbyts(bs,encode = 'utf_32_be')
        bs = b'\x00\x00\x4f\x60'
        decode_chbyts(bs,encode = 'utf_32_be')
    '''
    if('encode' in kwargs):
        encode=kwargs['encode']
    else:
        if('style' in kwargs):
            style = kwargs['style']
        else:
            style = 'js'
        if(style == 'js'):
            encode = 'utf_16_be'
        elif(style == 'py'):
            encode = 'raw_unicode_escape'
        else:
            encode = 'raw_unicode_escape'
    bs = remove_bom(bs,**kwargs)
    ch = bs.decode(encode)
    return(ch)

unpack_chbyts = decode_chbyts
byts2chstr = decode_chbyts

def get_bomtype(bs,**kwargs):
    '''
        #only support utf-16 utf-32 
        
        #LE           Little- Endian
        #BE           Big-Endian
        #OOB          Out-Of-Band (withour BOM)
        
        bs = b'\xff\xfe\x60\x4f'
        bs.decode('utf_16')
        get_bomtype(bs)
        '\u4f60'
        bs = b'\x60\x4f'
        bs.decode('utf_16_le')
        get_bomtype(bs)
        '\u4f60'
        bs = b'\xfe\xff\x4f\x60'
        get_bomtype(bs)
        decode_chbyts(bs,encode='utf_16_be')
        '\u4f60'
        bs = b'\x4f\x60'
        bs.decode('utf_16_be')
        get_bomtype(bs)
        '\u4f60'
        bs = b'\xff\xfe\x00\x00\x60\x4f\x00\x00'
        bs.decode('utf_32')
        get_bomtype(bs)
        '\U00004f60'
        bs = b'\x60\x4f\x00\x00'
        bs.decode('utf_32_le')
        get_bomtype(bs)
        '\U00004f60'
        bs = b'\x00\x00\xfe\xff\x00\x00\x4f\x60'
        decode_chbyts(bs,encode = 'utf_32_be')
        get_bomtype(bs)
        '\U00004f60'
        bs = b'\x00\x00\x4f\x60'
        bs.decode('utf_32_be')
        get_bomtype(bs)
        '\U00004f60'
    '''
    bominfo = get_bominfo(bs,**kwargs)
    return(bominfo[1])


#chstr                        char-string
#pack_chstr                   pack-char-string (to bytes-stream)
#chstr2byts                   pack-char-string (to bytes-stream)
#encode_chstr                 pack-char-string (to bytes-stream)
#chnum                        char-number
#pack_chnum                   pack-char-number (to bytes-stream)
#chnum2byts                   pack-char-number (to bytes-stream)
#encode_chnum                 pack-char-number (to bytes-stream)
#byts2chnum                   bytes-to-char-number

def pack_chstr(chstr,**kwargs):
    '''
        # most javascript use utf_16_be encode
        chstr = '问'
        pack_chstr(chstr)
        pack_chstr(chstr,style='py')
        pack_chstr(chstr,style='js')
        pack_chstr(chstr,encode = 'utf_16')
        pack_chstr(chstr,encode = 'utf_16_le')
    '''
    if('encode' in kwargs):
        encode=kwargs['encode']
    else:
        if('style' in kwargs):
            style = kwargs['style']
        else:
            style = 'js'
        if(style == 'js'):
            encode = 'utf_16_be'
        elif(style == 'py'):
            encode = 'raw_unicode_escape'
        else:
            encode = 'raw_unicode_escape'
    bs = chstr.encode(encode)
    return(bs)

chstr2byts = pack_chstr
encode_chstr = pack_chstr

def pack_chnum(chnum,**kwargs):
    '''
        # most javascript use utf_16_be encode
        chnum = 38382
        pack_chnum(chnum)
        pack_chnum(chnum,style='py')
        pack_chnum(chnum,style='js')
        pack_chnum(chnum,encode = 'utf_16')
        pack_chnum(chnum,encode = 'utf_16_le')
        
        '\u95ee'
    '''
    chstr = chr(chnum)
    bs = pack_chstr(chstr,**kwargs)
    return(bs)

chnum2byts = pack_chnum
encode_chnum = pack_chnum


def byts2chnum(bs,**kwargs):
    '''
        # most javascript use utf_16_be encode
        bs = b'\x95\xee'
        byts2chnum(bs)
        bs = b'\\u95ee'
        byts2chnum(bs,style='py')
        bs = b'\x95\xee'
        byts2chnum(bs,style='js')
        bs = b'\xff\xfe\xee\x95'
        byts2chnum(bs,encode = 'utf_16')
        bs = b'\xee\x95'
        chnum = byts2chnum(bs,encode = 'utf_16_le')
        chnum
        chr(chnum)
    '''
    chstr = decode_chbyts(bs,**kwargs)
    return(ord(chstr))
    

#decode_bytstrm       decode-bytes-stream (to string)
#bytstrm2str          decode-bytes-stream (to string)
#unpack_bytstrm       decode-bytes-stream (to string)

def decode_bytstrm(bs,**kwargs):
    '''
        bs = b'O`Y}T\x17'
        decode_bytstrm(bs)
        bs = b'O`Y}T\x17'
        decode_bytstrm(bs,style='js')
        bs = b'\\u4f60\\u597d\\u5417'
        decode_bytstrm(bs,style='py')
        bs = b'O`Y}T\x17'
        decode_bytstrm(bs,encode='utf_16_be')
        bs = b'\xff\xfe\x00\x00`O\x00\x00}Y\x00\x00\x17T\x00\x00'
        decode_bytstrm(bs,encode='utf_32')
        bs = b'\xe4\xbd\xa0\xe5\xa5\xbd\xe5\x90\x97'
        decode_bytstrm(bs,encode='utf_8')
    '''
    bs = remove_bom(bs)
    s = decode_chbyts(bs,**kwargs)
    return(s)

bytstrm2str = decode_bytstrm
unpack_bytstrm = decode_bytstrm


#@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@



#pack_str                pack-string
#encode_str              pack-string
#str2bytstrm             pack-string

def pack_str(s,**kwargs):
    '''
        s = '你好吗'
        pack_str(s)
        pack_str(s,style='js')
        pack_str(s,style='py')
        pack_str(s,encode='utf_16_be')
        pack_str(s,encode='utf_32')
        pack_str(s,encode='utf_8')
    '''
    return(pack_chstr(s,**kwargs))

encode_str = pack_str
str2bytstrm = pack_str


#str2hex                 string-in-hex
#hex2str                 hex-to-string
def str2hex(s,**kwargs):
    '''
        bs = b'O`N\xecY}\xd85\xdcR'
        s = bs.decode('utf_16_be')
        s
        str2hex(s,slashx=True)
        str2hex(s,slashx=False)
    '''
    bs = str2bytstrm(s,**kwargs)
    hs = bytstrm2hex(bs,**kwargs)
    return(hs)

def hex2str(hs,**kwargs):
    '''
        hs = '4f604eec597dd835dc52'
        hex2str(hs,style='js')
        hs = '\\x4f\\x60\\x4e\\xec\\x59\\x7d\\xd8\\x35\\xdc\\x52'
        hex2str(hs,style='js')
        hs = '\\x5c\\x75\\x34\\x66\\x36\\x30\\x5c\\x75\\x34\\x65\\x65\\x63\\x5c\\x75\\x35\\x39\\x37\\x64\\x5c\\x55\\x30\\x30\\x30\\x31\\x64\\x34\\x35\\x32'
        hex2str(hs,style='py')
        hs = '\\xe4\\xbd\\xa0\\xe4\\xbb\\xac\\xe5\\xa5\\xbd\\xf0\\x9d\\x91\\x92'
        hex2str(hs,encode='utf_8')
    '''
    bs = hex2bytstrm(hs,**kwargs)
    s = bytstrm2str(bs,**kwargs)
    return(s)

#str2chnums              string-to-char-numbers
#chnums2str              char-numbers-to-string
def str2chnums(s,**kwargs):
    '''
        s = '你好吗'
        cns = str2chnums(s)
        cns
    '''
    arr = list(s)
    cns = elel.array_map(arr,ord)
    return(cns)

def chnums2str(cns,**kwargs):
    '''
        cns = [20320, 22909, 21527]
        chnums2str(cns)
    '''
    arr = elel.array_map(cns,chr)
    s = elel.join(arr,'')
    return(s)


#str2bytnums             string-to-byte-numbers
#bytnums2str             byte-numbers-to-string
def str2bytnums(s,**kwargs):
    '''
        s = '你们好'
        str2bytnums(s)
        str2bytnums(s,style='js')
        str2bytnums(s,encode='utf_16_be')
        str2bytnums(s,style='py')
        str2bytnums(s,encode='raw_unicode_escape')
        str2bytnums(s,encode='utf_8')
    '''
    bs = str2bytstrm(s,**kwargs)
    bns = strm2bytnums(bs)
    return(bns)

def bytnums2str(bns,**kwargs):
    '''
        bns = [79, 96, 78, 236, 89, 125]
        bytnums2str(bns)
        bns = [79, 96, 78, 236, 89, 125]
        bytnums2str(bns,style='js')
        bns = [79, 96, 78, 236, 89, 125]
        bytnums2str(bns,encode='utf_16_be')
        bns = [92, 117, 52, 102, 54, 48, 92, 117, 52, 101, 101, 99, 92, 117, 53, 57, 55, 100]
        bytnums2str(bns,style='py')
        bns = [92, 117, 52, 102, 54, 48, 92, 117, 52, 101, 101, 99, 92, 117, 53, 57, 55, 100]
        bytnums2str(bns,encode='raw_unicode_escape')
        bns = [228, 189, 160, 228, 187, 172, 229, 165, 189]
        bytnums2str(bns,encode='utf_8')
    '''
    bs = bytnums2strm(bns)
    s = bytstrm2str(bs,**kwargs)
    return(s)

#str2us                  string-to-slashus
def str2us(s,**kwargs):
    '''
        bs = b'O`N\xecY}\xd85\xdcR'
        s = bs.decode('utf_16_be')
        s
        us = str2us(s,style='js')
        us
        slash_show(us,style='js')
        bs = b'\\u4f60\\u4eec\\u597d\\U0001d452'
        bs = b'\x5c\x75\x34\x66\x36\x30\x5c\x75\x34\x65\x65\x63\x5c\x75\x35\x39\x37\x64\x5c\x55\x30\x30\x30\x31\x64\x34\x35\x32'
        bs
        
        #上面两种格式的bytes 定义是一样的，只是显示方式不同
        #>>>bs = b'\x5c\x75\x34\x66\x36\x30\x5c\x75\x34\x65\x65\x63\x5c\x75\x35\x39\x37\x64\x5c\x55\x30\x30\x30\x31\x64\x34\x35\x32'
        #>>> bs
        #b'\\u4f60\\u4eec\\u597d\\U0001d452'
        #
        >>> hex(ord("\\"))
        '0x5c'
        >>> hex(ord("u"))
        '0x75'
        >>> hex(ord("4"))
        '0x34'
        >>> hex(ord("f"))
        '0x66'
        >>> hex(ord("6"))
        '0x36'
        >>> hex(ord("0"))
        '0x30'
        >>>
        >>> b'\\u4f60\\u4eec\\u597d\\U0001d452'.decode('raw_unicode_escape')
        '你们好𝑒'
        >>>

        s = bs.decode('raw_unicode_escape')
        s
        us = str2us(s,style='py')
        us
        slash_show(us,style='py')
    '''
    bs = str2bytstrm(s,**kwargs)
    us = bytstrm2us(bs,**kwargs)
    return(us)

#us2str                  slashus-to-string
def us2str(us,**kwargs):
    ''' 
        ####
        # unicode 的字面显示方式\\u \\U 总是BE 的 ，与实际存储方式无关:
            # >>> bs = '你'.encode('utf_16_le')
            # >>> bytstrm2hex(bs)
            # '\\x60\\x4f'
            # >>> bs = '你'.encode('utf_16_be')
            # >>> bytstrm2hex(bs)
            # '\\x4f\\x60'
            # >>>
        ####
        #py style
        us = '\\u4f60\\u4eec\\u597d\\U0001d452'
        s = us2str(us,style='py')
        s
        #js style
        us = '\\u4f60\\u4eec\\u597d\\ud835\\udc52'
        s = us2str(us,style='js')
        s
        ## by default ,is js style
        s = us2str(us)
        s
    '''
    if(us == ''):
        return("")
    else:
        bs = us2bytstrm(us,**kwargs)
        s = bytstrm2str(bs,**kwargs)
        return(s)




#byte-number                byte-number (number 0 -255)
#char-number                char-number  (ord(ch))
#str                        string
#bytstrm                    bytes-stream
#strmhex                    bytes-stream-in-hex
#bytnums                    byte-numbers-array (number 0-255)
#chnums                     char-numbers-array
#slashu                     unicode-in-slash ('\uxxxx' or '\Uxxxxxxxx')
#slashx                     asiic-in-slash ('\x??')

#所有转换都先转换为bytstrm

#bytstrm2hex                bytes-stream-to-stream-hex
#hex2bytstrm                stream-hex-to-bytes-stream
#strm2bytnums               bytes-stream-to-byte-numbers
#bytnums2strm               byte-numbers-to-stream
#bytstrm2chnums             bytes-stream-to-char-numbers
#chnums2bytstrm             char-numbers-to-bytes-stream
#bytstrm2us                 byte-stream-to-slashus
#us2bytstrm                 slashus-to-byte-stream


def slash_show(s,**kwargs):
    '''
        us = '\\x4f\\x60\\x59\\x7d\\x54\\x17'
        slash_show(us)
        us = '\\u4f60\\u4eec\\u597d'
        slash_show(us)
        us = '\\u4f60\\u4eec\\u597d\\U0001d452'
        slash_show(us)
        us = '\\u4f60\\u4eec\\u597d\\ud835\\udc52'
        slash_show(us,style='js')
    '''
    if('style' in kwargs):
        style = kwargs['style']
    else:
        style = 'py'
    if(style == 'py'):
        print(eval("'"+s+"'"))
    else:
        bs = us2bytstrm(s,style=style)
        s = bytstrm2str(bs)
        print(s)

def bytstrm2hex(bs,**kwargs):
    '''
        bs = b'O`Y}T\x17'
        hs = bytstrm2hex(bs)
        hs
        eval("'"+hs+"'")
        bytstrm2hex(bs,slashx=True)
        bytstrm2hex(bs,slashx=False)
    '''
    if('slashx' in kwargs):
        slashx = kwargs['slashx']
    else:
        slashx = True
    arr = elel.array_map(list(bs),hex)
    if(slashx):
        arr = elel.array_map(arr,str.replace,'0x','\\x')
    else:
        arr = elel.array_map(arr,str.replace,'0x','')
    h = elel.join(arr,'')
    return(h)

def hex2bytstrm(hs,**kwargs):
    '''
        hs = '4f60597d5417'
        hex2bytstrm(hs)
        hs = '\\x4f\\x60\\x59\\x7d\\x54\\x17'
        hex2bytstrm(hs)
    '''
    def cond_func(ele):
        num = int('0x'+ele,16)
        #important when ord >127 'latin-1' is different from 'utf-8'
        b = bytes(chr(num),'latin-1')
        return(b)
    hs = hs.replace('\\x','')
    arr = divide(hs,2)
    arr = elel.array_map(arr,cond_func)
    bs = elel.join(arr,b'')
    return(bs)

def strm2bytnums(bs,**kwargs):
    '''
        bs = b'O`Y}T\x17'
        bns = strm2bytnums(bs)
        bns
        elel.array_map(bns,chr)
    '''
    arr = list(bs)
    return(arr)

def bytnums2strm(bns,**kwargs):
    '''
        bns = [79, 96, 89, 125, 84, 23]
        bs = bytnums2strm(bns)
        bs
    '''
    arr = elel.array_map(bns,chr)
    s = elel.join(arr,'')
    bs = bytes(s,'latin-1')
    return(bs)

def bytstrm2chnums(bs,**kwargs):
    '''
        bs = b'O`Y}T\x17'
        cns = bytstrm2chnums(bs)
        cns
        elel.array_map(cns,chr)
        cns = bytstrm2chnums(bs,encode='utf_16_be')
        cns
        elel.array_map(cns,chr)
        cns = bytstrm2chnums(bs,style='js')
        cns
        elel.array_map(cns,chr)
        bs = b'\\u4f60\\u597d\\u5417'
        bs.__len__()
        cns = bytstrm2chnums(bs,style='py')
        cns
        elel.array_map(cns,chr)
        bs = b'\xe4\xbd\xa0\xe5\xa5\xbd\xe5\x90\x97'
        cns = bytstrm2chnums(bs,encode='utf_8')
        cns
        elel.array_map(cns,chr)
    '''
    if('encode' in kwargs):
        encode=kwargs['encode']
    else:
        if('style' in kwargs):
            style = kwargs['style']
        else:
            style = 'js'
        if(style == 'js'):
            encode = 'utf_16_be'
        elif(style == 'py'):
            encode = 'raw_unicode_escape'
        else:
            encode = 'raw_unicode_escape'
    s = bs.decode(encode)
    uarr = list(s)
    cns = elel.array_map(uarr,ord)
    return(cns)

strm2chnums = bytstrm2chnums

def chnums2bytstrm(cns,**kwargs):
    '''
        cns = [20320, 22909, 21527]
        bs = chnums2bytstrm(cns)
        bs
        
        chnums2bytstrm(cns,style='js')
        chnums2bytstrm(cns,encode='utf_16_be')
        
        
        chnums2bytstrm(cns,style='py')
        chnums2bytstrm(cns,encode='raw_unicode_escape')
        
        chnums2bytstrm(cns,encode='utf_8')
        
        
    '''
    if('encode' in kwargs):
        encode=kwargs['encode']
    else:
        if('style' in kwargs):
            style = kwargs['style']
        else:
            style = 'js'
        if(style == 'js'):
            encode = 'utf_16_be'
        elif(style == 'py'):
            encode = 'raw_unicode_escape'
        else:
            encode = 'raw_unicode_escape'
    s = chnums2str(cns,**kwargs)
    bs = str2bytstrm(s,**kwargs)
    return(bs)

chnums2strm = chnums2bytstrm

def bytstrm2us(bs,**kwargs):
    '''
        bs = b'O`N\xecY}\xd85\xdcR'
        bs.decode('utf_16_be')
        us = bytstrm2us(bs,style='js')
        us
        slash_show(us,style='js')
        bs = b'\\u4f60\\u4eec\\u597d\\U0001d452'
        bs = b'\x5c\x75\x34\x66\x36\x30\x5c\x75\x34\x65\x65\x63\x5c\x75\x35\x39\x37\x64\x5c\x55\x30\x30\x30\x31\x64\x34\x35\x32'
        bs
        #上面两种格式的bytes 定义是一样的，只是显示方式不同
        #>>>bs = b'\x5c\x75\x34\x66\x36\x30\x5c\x75\x34\x65\x65\x63\x5c\x75\x35\x39\x37\x64\x5c\x55\x30\x30\x30\x31\x64\x34\x35\x32'
        #>>> bs
        #b'\\u4f60\\u4eec\\u597d\\U0001d452'
        bs.decode('raw_unicode_escape')
        bns = list(bs)
        bns
        bytnums2hex(bns)
        us = bytstrm2us(bs,style='py')
        us
        slash_show(us,style='py')
    '''
    if('encode' in kwargs):
        encode=kwargs['encode']
    else:
        if('style' in kwargs):
            style = kwargs['style']
        else:
            style = 'js'
        if(style == 'js'):
            encode = 'utf_16_be'
        elif(style == 'py'):
            encode = 'raw_unicode_escape'
        else:
            encode = 'raw_unicode_escape'
    src = bs.__str__()
    cond1 = ('\\u' in src)
    cond2 = ('\\U' in src)
    cond = (cond1 | cond2)
    if(cond):
        us = src[2:-1]
        us=us.replace('\\\\','\\')
    else:
        if('style' in kwargs):
            style = kwargs['style']
        else:
            style = 'js'
        if(style == 'js'):
            cns = bytstrm2chnums(bs,**kwargs)
            hs = chnums2hex(cns,slashx=False)
            arr =  divide(hs,4)
            arr = list(map('{:0>4}'.format,arr))
            def cond_func(ele):
                return('\\u'+ele)
            arr = elel.array_map(arr,cond_func)
            us = elel.join(arr,'')
        else:
            bs = bs.decode(encode).encode('raw_unicode_escape')
            src = bs.__str__()
            us = src[2:-1]
            us=us.replace('\\\\','\\')    
    return(us)

def us2bytstrm(us,**kwargs):
    ''' 
        ####
        # unicode 的字面显示方式\\u \\U 总是BE 的 ，与实际存储方式无关:
            # >>> bs = '你'.encode('utf_16_le')
            # >>> bytstrm2hex(bs)
            # '\\x60\\x4f'
            # >>> bs = '你'.encode('utf_16_be')
            # >>> bytstrm2hex(bs)
            # '\\x4f\\x60'
            # >>>
        ####
        #py style
        us = '\\u4f60\\u4eec\\u597d\\U0001d452'
        slash_show(us)
        bs = us2bytstrm(us,style='py')
        bs
        bs.__len__()
        bytstrm2hex(bs)
        bs.decode('raw_unicode_escape')
        #js style
        us = '\\u4f60\\u4eec\\u597d\\ud835\\udc52'
        slash_show(us,style='js')
        bs = us2bytstrm(us,style='js')
        bs
        bs.__len__()
        bytstrm2hex(bs)
        bs.decode('utf_16_be')
        ## by default ,is js style
        bs = us2bytstrm(us)
        bs
        bs.__len__()
        bytstrm2hex(bs)
        decode_bytstrm(bs)
    '''
    if('encode' in kwargs):
        encode=kwargs['encode']
    else:
        if('style' in kwargs):
            style = kwargs['style']
        else:
            style = 'js'
        if(style == 'js'):
            encode = 'utf_16_be'
        elif(style == 'py'):
            encode = 'raw_unicode_escape'
        else:
            encode = 'raw_unicode_escape'
    if('style' in kwargs):
        style = kwargs['style']
    else:
        style = 'js'
    if(style == 'js'):
        us = str.lower(us)
        uarr = us.split('\\u')
        uarr.pop(0)
        barr = []
        for i in range(0,uarr.__len__()):
            tmp = divide(uarr[i],2)
            barr.extend(tmp)
        hs = elel.join(barr,'')
        bs = hex2bytstrm(hs)
    else:
        bs = bytes(us,encode)
    return(bs)



#hex 

#bytnums2hex              byte-numbers-in-hex
#hex2bytnums              hex-to-byte-numbers
def bytnums2hex(bns,**kwargs):
    '''
        bns = [92, 117, 52, 102, 54, 48, 92, 117, 52, 101, 101, 99, 92, 117, 53, 57, 55, 100, 92, 85, 48, 48, 48, 49, 100, 52, 53, 50]
        bytnums2hex(bns)
        
        bs = b'\\u4f60\\u4eec\\u597d\\U0001d452'
        bs.__len__()
        list(bs)
        #bytes  取下标 会被隐式转换
        bs[0]
        type(bs[0])
        bs[1]
        #...
        bs[27]
        
        bytnums2hex(bns,slashx=False)
        
    '''
    if('slashx' in kwargs):
        slashx = kwargs['slashx']
    else:
        slashx = True
    arr = elel.array_map(bns,hex)
    hs = elel.join(arr,'')
    hs = str.lower(hs)
    if(slashx == True):
        hs = hs.replace('0x','\\x')
    else:
        hs = hs.replace('0x','')
    return(hs)

def hex2bytnums(hs,**kwargs):
    '''
        hs = '\\x5c\\x75\\x34\\x66\\x36\\x30\\x5c\\x75\\x34\\x65\\x65\\x63\\x5c\\x75\\x35\\x39\\x37\\x64\\x5c\\x55\\x30\\x30\\x30\\x31\\x64\\x34\\x35\\x32'
        hex2bytnums(hs)
        hs = '5c75346636305c75346565635c75353937645c553030303164343532'
        hex2bytnums(hs)
    '''
    hs = str.lower(hs)
    hs = hs.replace('\\x','')
    arr = divide(hs,2)
    def cond_func(ele):
        ele='0x'+ele
        ele = int(ele,16)
        return(ele)
    arr = elel.array_map(arr,cond_func)    
    return(arr)


#chnums2hex               char-numbers-in-hex
#hex2chnums               hex-to-char-numbers

def chnums2hex(cns,**kwargs):
    '''
        cns = [20320, 20204, 22909, 119890]
        chnums2hex(cns)
        chnums2hex(cns,slashx=False)
        chnums2hex(cns,style='js')
        chnums2hex(cns,style='py')
        chnums2hex(cns,encode='raw_unicode_escape')
        chnums2hex(cns,encode='utf_8')
    '''
    if('encode' in kwargs):
        encode=kwargs['encode']
    else:
        if('style' in kwargs):
            style = kwargs['style']
        else:
            style = 'js'
        if(style == 'js'):
            encode = 'utf_16_be'
        elif(style == 'py'):
            encode = 'raw_unicode_escape'
        else:
            encode = 'raw_unicode_escape'
    if('slashx' in kwargs):
        slashx = kwargs['slashx']
    else:
        slashx = True
    hs = bytstrm2hex(chnums2bytstrm(cns,**kwargs),slashx=slashx)
    return(hs)

def hex2chnums(hs,**kwargs):
    '''
        hs = '\\x4f\\x60\\x4e\\xec\\x59\\x7d\\xd8\\x35\\xdc\\x52'
        chnums = hex2chnums(hs)
        chnums
        hs = '4f604eec597dd835dc52'
        chnums = hex2chnums(hs)
        chnums
        hs = '\\x4f\\x60\\x4e\\xec\\x59\\x7d\\xd8\\x35\\xdc\\x52'
        chnums = hex2chnums(hs,style='js')
        chnums
        hs = '\\x5c\\x75\\x34\\x66\\x36\\x30\\x5c\\x75\\x34\\x65\\x65\\x63\\x5c\\x75\\x35\\x39\\x37\\x64\\x5c\\x55\\x30\\x30\\x30\\x31\\x64\\x34\\x35\\x32'
        chnums = hex2chnums(hs,style='py')
        chnums
        hs = '\\x5c\\x75\\x34\\x66\\x36\\x30\\x5c\\x75\\x34\\x65\\x65\\x63\\x5c\\x75\\x35\\x39\\x37\\x64\\x5c\\x55\\x30\\x30\\x30\\x31\\x64\\x34\\x35\\x32'
        chnums = hex2chnums(hs,encode='raw_unicode_escape')
        chnums
        hs = '\\xe4\\xbd\\xa0\\xe4\\xbb\\xac\\xe5\\xa5\\xbd\\xf0\\x9d\\x91\\x92'
        chnums = hex2chnums(hs,encode='utf_8')
        chnums
    '''
    bs = hex2bytstrm(hs,**kwargs)
    chnums = bytstrm2chnums(bs,**kwargs)
    return(chnums)


#hex2us                   hex-to-slashus
#us2hex                   slashus-to-hex

def hex2us(hs,**kwargs):
    '''
        hs = '4f604eec597dd835dc52'
        us = hex2us(hs,style='js')
        us
        slash_show(us,style='js')
        
        hs = '\\x5c\\x75\\x34\\x66\\x36\\x30\\x5c\\x75\\x34\\x65\\x65\\x63\\x5c\\x75\\x35\\x39\\x37\\x64\\x5c\\x55\\x30\\x30\\x30\\x31\\x64\\x34\\x35\\x32'
        us = hex2us(hs,style='py')
        us
        slash_show(us,style='py')
        
    '''
    bs = hex2bytstrm(hs,**kwargs)
    us = bytstrm2us(bs,**kwargs)
    return(us)

def us2hex(us,**kwargs):
    '''
        us = '\\u4f60\\u4eec\\u597d\\ud835\\udc52'
        us2hex(us,style='js')
        us = '\\u4f60\\u4eec\\u597d\\U0001d452'
        us2hex(us,style='py')
    '''
    bs = us2bytstrm(us,**kwargs)
    hs = bytstrm2hex(bs,**kwargs)
    return(hs)


#chnums2bytnums           char-numbers-to-byte-numbers
#bytnums2chnums           byte-numbers-to-char-numbers


def chnums2bytnums(cns,**kwargs):
    '''
        cns = [20320, 22909, 21527]
        chnums2bytnums(cns)
        
        chnums2bytnums(cns,style='js')
        chnums2bytnums(cns,encode='utf_16_be')
        
        
        chnums2bytnums(cns,style='py')
        chnums2bytnums(cns,encode='raw_unicode_escape')
        
        chnums2bytnums(cns,encode='utf_8')
    '''
    bs = chnums2bytstrm(cns,**kwargs)
    bns = strm2bytnums(bs,**kwargs)
    return(bns)

def bytnums2chnums(bns,**kwargs):
    '''
        bns = [79, 96, 89, 125, 84, 23]
        bytnums2chnums(bns,style='js')
        bns = [92, 117, 52, 102, 54, 48, 92, 117, 53, 57, 55, 100, 92, 117, 53, 52, 49, 55]
        bytnums2chnums(bns,style='py')
        bns = [228, 189, 160, 229, 165, 189, 229, 144, 151]
        bytnums2chnums(bns,encode='utf_8')
    '''
    bs = bytnums2strm(bns,**kwargs)
    cns = bytstrm2chnums(bs,**kwargs)
    return(cns)

#chnums2us                char-numbers-to-slashus
#us2chnums                slashus-to-char-numbers

def chnums2us(cns,**kwargs):
    '''
        cns = [20320, 22909, 21527,119890]
        us = chnums2us(cns,style='js')
        us
        slash_show(us,style='js')
        us = chnums2us(cns,style='py')
        us
        slash_show(us,style='py')
    '''
    bs = chnums2bytstrm(cns,**kwargs)
    us = bytstrm2us(bs,**kwargs)
    return(us)

def us2chnums(us,**kwargs):
    '''
        us = '\\u4f60\\u597d\\u5417\\ud835\\udc52'
        us2chnums(us,style='js')
        us = '\\u4f60\\u597d\\u5417\\U0001d452'
        us2chnums(us,style='py')
        
    '''
    bs = us2bytstrm(us,**kwargs)
    cns = bytstrm2chnums(bs,**kwargs)
    return(cns)

#bytnums2us               byte-numbers-to-slashus
#us2bytnums               slashus-to-byte-numbers

def bytnums2us(bns,**kwargs):
    '''
        bns = [79, 96, 89, 125, 84, 23, 216, 53, 220, 82]
        us = bytnums2us(bns,style='js')
        us 
        slash_show(us,style='js')
        bns = [92, 117, 52, 102, 54, 48, 92, 117, 53, 57, 55, 100, 92, 117, 53, 52, 49, 55, 92, 85, 48, 48, 48, 49, 100, 52, 53, 50]
        us = bytnums2us(bns,style='py')
        us 
        slash_show(us,style='py')
    '''
    bs = bytnums2strm(bns,**kwargs)
    us = bytstrm2us(bs,**kwargs)
    return(us)


def us2bytnums(us,**kwargs):
    '''
        us = '\\u4f60\\u597d\\u5417\\ud835\\udc52'
        us2bytnums(us,style='js')
        us = '\\u4f60\\u597d\\u5417\\U0001d452'
        us2bytnums(us,style='py')
        
    '''
    bs = us2bytstrm(us,**kwargs)
    bns = strm2bytnums(bs,**kwargs)
    return(bns)


def str_code_points(s,**kwargs):
    '''
        bs = b'\xd85\xdcRO`N\xecY}\xd85\xdcR'
        s = bs.decode('utf_16_be')
        s
        str_code_points(s,style='js')
        bs[0:4]
        bs[0:4].decode('utf_16_be')
        bs[4:6]
        bs[4:6].decode('utf_16_be')
        bs[8:10]
        bs[8:10].decode('utf_16_be')
        bs[10:14]
        bs[10:14].decode('utf_16_be')
        #
        bs = s.encode('utf_8')
        str_code_points(s,encode='utf_8')
        bs[0:4]
        bs[0:4].decode('utf_8')
        bs[4:7]
        bs[4:7].decode('utf_8')
        bs[7:10]
        bs[7:10].decode('utf_8')
        bs[10:13]
        bs[10:13].decode('utf_8')
        bs[13:17]
        bs[13:17].decode('utf_8')
    '''
    if('encode' in kwargs):
        encode=kwargs['encode']
    else:
        if('style' in kwargs):
            style = kwargs['style']
        else:
            style = 'js'
        if(style == 'js'):
            encode = 'utf_16_be'
        elif(style == 'py'):
            encode = 'raw_unicode_escape'
        else:
            encode = 'raw_unicode_escape'
    arr = list(s)
    locs = [0]
    cursur = 0
    lngth = arr.__len__()
    for i in range(0,lngth):
        chbs = encode_chstr(arr[i],encode=encode)
        offset = chbs.__len__()
        cursur = cursur + offset
        locs.append(cursur)
    return(locs)

#
def str_jschar_points(s):
    '''
        bs = b'\xd85\xdcRO`N\xecY}\xd85\xdcR'
        s = bs.decode('utf_16_be')    
        s 
        str2jscharr(s)
    '''
    locs = str_code_points(s,encode='utf_16_be')
    locs = elel.array_map(locs,lambda ele:ele//2)
    return(locs)

def pychpoints2jscharpoints(s,pypoint):
    '''
        bs = b'\xd85\xdcRO`N\xecY}\xd85\xdcR'
        s = bs.decode('utf_16_be')    
        s 
        str2jscharr(s)
        pychpoints2jscharpoints(s,0)
        pychpoints2jscharpoints(s,1)
        pychpoints2jscharpoints(s,2)
        pychpoints2jscharpoints(s,3)
    '''
    jslocs = str_jschar_points(s)
    return(jslocs[pypoint])

def jscharpoints2pychpoints(s,jspoint):
    '''
        bs = b'\xd85\xdcRO`N\xecY}\xd85\xdcR'
        s = bs.decode('utf_16_be')    
        s 
        str2jscharr(s)
        jscharpoints2pychpoints(s,0)
        jscharpoints2pychpoints(s,2)
        jscharpoints2pychpoints(s,3)
        jscharpoints2pychpoints(s,4)
        jscharpoints2pychpoints(s,5)
        jscharpoints2pychpoints(s,7)
    '''
    jslocs = str_jschar_points(s)
    return(jslocs.index(jspoint))


def us2uarr(us,**kwargs):
    '''
        us = '\\u4f60\\u597d\\u5417\\ud835\\udc52'
        us2uarr(us,mode='prefix')
        us2uarr(us,mode='value')
        us2uarr(us)
        us = '\\u4f60\\u597d\\u5417\\U0001d452'
        us2uarr(us,mode='prefix')
        us2uarr(us,mode='value')
        us2uarr(us)
    '''
    if('mode' in kwargs):
        mode = kwargs['mode']
    else:
        mode = 'both'
    regex = re.compile('(\\\\[u|U][0-9a-fA-F]+)')
    m = regex.findall(us)
    lngth = m.__len__()
    prefixes = []
    values = []
    bothes = []
    for i in range(0,lngth):    
        pfix = m[i][:2]    
        value = m[i][2:]    
        prefixes.append(pfix)
        values.append(value)
        bothes.append((pfix,value))
    if(mode == 'prefix'):
        return(prefixes)
    elif(mode == 'value'):
        return(values)
    else:
        return(bothes)

def uarr2us(*args):
    '''
        puarr = ['\\u', '\\u', '\\u', '\\U']
        vuarr = ['4f60', '597d', '5417', '0001d452']
        uarr2us(puarr,vuarr)
        uarr = [('\\u', '4f60'), ('\\u', '597d'), ('\\u', '5417'), ('\\U', '0001d452')]
        uarr2us(uarr)
    '''
    uarr = args[0]
    lngth = list(uarr).__len__()
    if(lngth<1):
        return('')
    else:
        pass
    if(type(uarr[0])==type((0,0))):
        def cond_func(ele):
            return(ele[0]+ele[1])
        uarr = elel.array_map(uarr,cond_func)
    else:
        puarr = args[0]
        vuarr = args[1]
        def map_func(ele1,ele2):
            return(ele1+ele2)
        uarr = elel.array_map2(puarr,vuarr,map_func=map_func)
    us = elel.join(uarr,'')
    return(us)


def uarr2jscharr(*args):
    '''
        uarr = ['4f60', '4eec', '597d', 'd835', 'dc52']
        uarr2jscharr(uarr)
    '''
    uarr = args[0]
    lngth = list(uarr).__len__()
    if(lngth<1):
        return([])
    else:
        pass
    if(type(uarr[0])==type((0,0))):
        def cond_func(ele):
            return(ele[1])
        uarr = elel.array_map(uarr,cond_func)
    else:
        pass
    def cond_func(ele):
        ele = '0x'+ele    
        n = int(ele,16)    
        return(chr(n))    
    jscharr = elel.array_map(uarr,cond_func)
    return(jscharr)

def uarr2str(*uarrs,**kwargs):
    '''
        puarr = ['\\u', '\\u', '\\u', '\\U']
        vuarr = ['4f60', '597d', '5417', '0001d452']    
        uarr2str(puarr,vuarr,style='py')    
        uarr = [('\\u', '4f60'), ('\\u', '597d'), ('\\u', '5417'), ('\\U', '0001d452')]    
        uarr2str(uarr,style='py')    
    '''
    us = uarr2us(*uarrs)
    s = us2str(us,**kwargs)
    return(s)

def str2uarr(s,**kwargs):
    '''
        bs = b'\xd85\xdcRO`N\xecY}\xd85\xdcR'
        s = bs.decode('utf_16_be')
        s
        str2uarr(s,mode='both')
        str2uarr(s,mode='value')
    '''
    us = str2us(s,**kwargs)
    uarr = us2uarr(us,**kwargs)
    return(uarr)

def str2jscharr(s,**kwargs):
    '''
        bs = b'\xd85\xdcRO`N\xecY}\xd85\xdcR'
        s = bs.decode('utf_16_be')
        s
        str2jscharr(s)
    '''
    uarr = str2uarr(s,mode='both')
    jscharr = uarr2jscharr(uarr)
    return(jscharr)


#strlen                string-length

def length(s,**kwargs):
    '''
        # in python , the string-length means  unicode-char-lngth 
        # in javascript, the length means how-many 16-bit unit
        # for example:
        # run in js 
        var p = '\ud835\udc52' 
        p 
        p.length 
        p.codePointAt(0)    
        p.codePointAt(0).toString(16)
        p.charCodeAt(0).toString(16)
        p.charCodeAt(1).toString(16)
        '\ud835\udc52'
        # codePointAt(0) similiar to  ord in python
        
        chr(119890)
        ord(chr(119890))
        hex(119890)
        
        length(chr(119890))
        length(chr(119890),style='js')
    '''
    if('style' in kwargs):
        style = kwargs['style']
    else:
        style = 'py'
    if(style == 'py'):
        lngth = s.__len__()
    else:
        bs = s.encode('utf_16_be')
        q = bs.__len__() // 2
        r = bs.__len__() % 2
        if(r == 0):
            lngth = q
        else:
            lngth = q + 1
    return(lngth)

def fromCharCode(*args,**kwargs):
    '''
        #by default, the style is 'js'
        
        fromCharCode(97,98,99)
        fromCharCode(97,98,99,style='js')
        fromCharCode(97,98,99,style='py')
        
        #in javascript , only keep the low 2 bytes
        # String['fromCharCode'](270752) = String['fromCharCode'](0x421a0)
        # 0x000421a0
        # 0x    21a0 = 8608
        # So:
        # String['fromCharCode'](270752) = String['fromCharCode'](8608) = '?'
        
        fromCharCode(270752,style='js')
        fromCharCode(270752,style='py')
        fromCharCode(8608,style='js')
        fromCharCode(8608,style='py')
    '''
    if('style' in kwargs):
        style = kwargs['style']
    else:
        style = 'js'
    rslt =''
    if(style == 'py'):
        for i in range(0,args.__len__()):
            rslt = rslt + chr(args[i])
    else:
        for i in range(0,args.__len__()):
            rslt = rslt + chr(0x0000ffff & args[i])
    return(rslt)

def fromCodePoint(*args,**kwargs):
    '''
        # refer to https://developer.mozilla.org/zh-CN/docs/Web/JavaScript/Reference/Global_Objects/String/fromCharCode
        fromCodePoint(42)       
        fromCodePoint(65, 90)   
        fromCodePoint(0x404)    
        fromCodePoint(0x2F804)  
        fromCodePoint(194564)   
        fromCodePoint(0x1D306, 0x61, 0x1D307) 
    '''
    if('encode' in kwargs):
        encode=kwargs['encode']
    else:
        if('style' in kwargs):
            style = kwargs['style']
        else:
            style = 'js'
        if(style == 'js'):
            encode = 'utf_16_be'
        elif(style == 'py'):
            encode = 'raw_unicode_escape'
        else:
            encode = 'utf_16_be'
    def cond_func(ele,encode='utf_16_be',style='js'):
        bs = pack_chnum(ele,encode = encode,style=style)
        ckstr = bs.decode(encode)
        return(ckstr)
    args = list(args)
    arr = elel.array_map(args,cond_func,encode,style)
    s = elel.join(arr,'')
    return(s)

def charAt(s,index=0,**kwargs):
    '''
        bs = b'O`N\xecY}\xd85\xdcR'
        s = bs.decode('utf_16_be')
        s
        bytstrm2us(bs,style='js')
        #refer to js ,js 不是按照char-length 算位置的，而是按照16-bit 
        #s = '\u4f60\u4eec\u597d\ud835\udc52'
        #"你们好??"
        #s.charAt(0)
        #"你"
        #s.charAt(1)
        #"们"
        #s.charAt(2)
        #"好"
        #s.charAt(3)
        #"\ud835"
        #s.charAt(4)
        #"\udc52"
        #arr = Array.from(s)
        #Array(4) [ "你", "们", "好", "??" ]
        charAt(s,3)
        charAt(s,3,style='py')
        charAt(s,3,style='js')
        charAt(s,4,style='js')
        #by default ,index = 0
        charAt(s)
        
    '''
    if('style' in kwargs):
        style = kwargs['style']
    else:
        style = 'py'
    if(style == 'py'):
        ch = s[index]
    else:
        us = str2us(s,style='js')
        uarr = us.split('\\u')
        uarr.pop(0)
        tmp = '0x' + uarr[index]
        cn = int(tmp,16)
        ch = chr(cn)
    return(ch)

def charCodeAt(s,index=0,**kwargs):
    '''
        bs = b'O`N\xecY}\xd85\xdcR'
        s = bs.decode('utf_16_be')
        s
        bytstrm2us(bs,style='js')
        #refer to js ,js 不是按照char-length 算位置的，而是按照16-bit 
        #s = '\u4f60\u4eec\u597d\ud835\udc52'
        #"你们好??"
        #s.charCodeAt(0)
        #20320
        #s.charCodeAt(1)
        #20204
        #s.charCodeAt(2)
        #22909
        #s.charCodeAt(3)
        #55349
        #s.charCodeAt(4)
        #56402
        #arr = Array.from(s)
        #Array(4) [ "你", "们", "好", "??" ]
        charCodeAt(s,3)
        charCodeAt(s,3,style='py')
        charCodeAt(s,3,style='js')
        charCodeAt(s,4,style='js')
        #by default ,index = 0
        charCodeAt(s)
        
    '''
    if('style' in kwargs):
        style = kwargs['style']
    else:
        style = 'py'
    return(ord(charAt(s,index,**kwargs)))

def codePointAt(s,index=0,**kwargs):
    '''
        bs = b'\xd85\xdcRO`N\xecY}\xd85\xdcR'
        s = bs.decode('utf_16_be')
        s
        bytstrm2us(bs,style='js')
        #refer to js ,js 不是按照char-length 算位置的，而是按照16-bit 
        codePointAt(s,0,style='py')
        codePointAt(s,1,style='py')
        codePointAt(s,2,style='py')
        codePointAt(s,3,style='py')
        codePointAt(s,4,style='py')
        #
        codePointAt(s,0,style='js')
        codePointAt(s,1,style='js')
        codePointAt(s,2,style='js')
        codePointAt(s,3,style='js')
        codePointAt(s,4,style='js')
        codePointAt(s,5,style='js')
        codePointAt(s,6,style='js')
        #by default ,index = 0
        codePointAt(s)
        
    '''
    if('style' in kwargs):
        style = kwargs['style']
    else:
        style = 'py'
    if(style == 'py'):
        return(ord(charAt(s,index,**kwargs)))
    else:
        locs = str_code_points(s,encode='utf_16_be')
        locs = elel.array_map(locs,lambda ele:ele//2)
        uarr = str2uarr(s,**kwargs)
        jscharr = uarr2jscharr(uarr)
        if(index in locs):
            return(ord(charAt(s,locs.index(index),style='py')))
        else:
            return(ord(jscharr[index]))

def concat(*args,**kwargs):
    '''
        concat('abc','efg','sss')
    '''
    args = list(args)
    def callback(acc,curr):
        acc = acc+curr
        return(acc)
    s = elel.reduce_left(args,callback,"")
    return(s)

def endsWith(s,suffix,end=None,start=0):
    '''
        s = "To be, or not to be, that is the question."
        endsWith(s,"question.")
        endsWith(s,"to be")
        s[:19]
        endsWith(s,"to be",19)
        s[:5]
        endsWith(s,"to be",5)
    '''
    if(end == None):
        end = s.__len__()
    else:
        pass
    return(str.endswith(s,suffix,start,end))

def includes(s1,s2,start=0):
    '''
    '''
    cond = (s2 in s1[start:])
    return(cond)

def indexOf(s,value,fromIndex=0,end=None):
    '''
    '''
    if(end == None):
        end = s.__len__()
    else:
        pass
    return(s[fromIndex:end].index(value))

def lastIndexOf(s,value,fromIndex=0,end=None):
    '''
        lastIndexOf("acccfad","a")
    '''
    if(end == None):
        end = s.__len__()
    else:
        pass
    return(elel.lastIndexOf(s[fromIndex:end],value))

def padEnd(s1,targetLength,s2="\x20"):
    '''
        padEnd('abc',10)
        padEnd('abc',10,'foo')
        padEnd('abc',6,'123456')
        padEnd('abc',1)
    '''
    s1lngth = s1.__len__()
    s2lngth = s2.__len__()
    rpts = (targetLength - s1lngth)// s2lngth + 1
    s = s1 + s2 * rpts
    if(targetLength>=s1lngth):
        s = s[:targetLength]
    else:
        s = s1
    return(s)

def padStart(s1,targetLength,s2="\x20"):
    '''
        padStart('abc',10)
        padStart('abc',10,'foo')
        padStart('abc',6,'123456')
        padStart('abc',1)
    '''
    s1lngth = s1.__len__()
    s2lngth = s2.__len__()
    rpts = (targetLength - s1lngth)// s2lngth + 1
    s = s2 * rpts + s1
    if(targetLength>=s1lngth):
        s = s[:targetLength]
    else:
        s = s1
    return(s)

#@@@@
def repeat(s,times):
    return(s*times)


def replace_seqs_at(s,locs,values):
    arr = list(s)
    locs = list(locs)
    for i in range(locs.__len__()):
        loc = locs[i]
        arr[loc] = values[i]
    return(elel.join(arr,""))


def replace_newsub_parser(params):
    '''
        params = 'abc$$ef$&oo'
        desc_arr = replace_newsub_parser(params)
        pobj(desc)
        params = 'abc$$ef$&$2'
        desc_arr = replace_newsub_parser(params)
        pobj(desc_arr)
    '''
    s = params
    ####
    if(s == ''):
        return('')
    else:
        pass
    ####
    lngth = s.__len__()
    rslt = []
    desc = {
        'type':None,
        'range':None,
        'attrib':None,
    }
    states = ['init','do','so','dc','mc','lc','rc','no']
    rslt = []
    si = 0
    ei = 0
    state = 'init'
    input = s[0]
    numbuf =''
    if(s[0] == '$'):
        state = 'do'
    else:
        state = 'so'
    for i in range(1,lngth):
        input = s[i]
        if(state == 'do'):
            if(input == '$'):
                state = 'dc'
            elif(input == '&'):
                state = 'mc'
            elif(input == "`"):
                state = 'lc'
            elif(input == "'"):
                state = 'rc'
            elif(input in "0123456789"):
                numbuf = input
                state = 'no'
            else:
                raise Exception("input error only '$$','$&','$`','$','$n',permited")
        elif(state == 'so'):
            if(input == '$'):
                #close so
                ei = i 
                d = copy.deepcopy(desc)
                d['range'] = (si,ei)
                d['attrib'] = s[si:ei]
                d['type'] = 'str'
                rslt.append(d)
                si = ei
                state = 'do'
            else:
                #continue collect s
                pass
        else:
            if("c" in state):
                ei = i 
                d = copy.deepcopy(desc)
                d['range'] = (si,ei)
                if(state == 'dc'):
                    d['type'] = 'dollar'
                    d['attrib'] = '$'
                elif(state == 'mc'):
                    d['type'] = 'match'
                elif(state == 'lc'):
                    d['type'] = 'left'
                elif(state == 'rc'):
                    d['type'] = 'right'
                if(input == '$'):
                    #goto do
                    state = 'do'
                else:
                    #goto so
                    state = 'so'
                rslt.append(d)
                si = ei
            elif(state == 'no'):
                if(input == '$'):
                    ei = i 
                    d = copy.deepcopy(desc)
                    d['range'] = (si,ei)
                    d['type'] = 'num'
                    d['attrib'] = int(numbuf)
                    numbuf = ''
                    state = 'do'
                    rslt.append(d)
                    si = ei
                elif(input in "0123456789"):
                    numbuf = numbuf + input
                else:
                    ei = i 
                    d = copy.deepcopy(desc)
                    d['range'] = (si,ei)
                    d['type'] = 'num'
                    d['attrib'] = int(numbuf)
                    numbuf = ''
                    state = 'do'
                    rslt.append(d)
                    si = ei
            else:
                raise Exception('state error')
    ####
    if(lngth == 1):
        i = 0
    else:
        pass
    ####
    if(state == 'so'):
        ei = i + 1
        d = copy.deepcopy(desc)
        d['range'] = (si,ei)
        d['type'] = 'str'
        d['attrib'] = s[si:ei]
        rslt.append(d)
    elif('c' in state):
        ei = i + 1 
        d = copy.deepcopy(desc)
        d['range'] = (si,ei)
        if(state == 'dc'):
            d['type'] = 'dollar'
            d['attrib'] = '$'
        elif(state == 'mc'):
            d['type'] = 'match'
        elif(state == 'lc'):
            d['type'] = 'left'
        elif(state == 'rc'):
            d['type'] = 'right'
        rslt.append(d)
    elif(state == 'no'):
        ei = i + 1
        d = copy.deepcopy(desc)
        d['range'] = (si,ei)
        d['type'] = 'num'
        d['attrib'] = int(numbuf)
        numbuf = ''
        rslt.append(d)
    else:
        raise Exception('state error')
    return(rslt)

def replace_creat_newsub(params,match,groups,left,right):
    '''
        params = 'UUU$$EE$&$1'
        
        s = '^^^abc12345#$*%tail'
        regex = re.compile("([a-z]+)(\d*)([^\w]*)")
        m = regex.search(s)
        match = m.group(0)
        match
        left = s[:m.start()]
        left
        right = s[m.end():]
        right
        groups = m.groups()
        groups
        offset = m.start()
        offset
        replace_creat_newsub(params,match,groups,left,right)
    '''
    desc_arr = replace_newsub_parser(params)
    rslt = ''
    for i in range(0,desc_arr.__len__()):
        desc = desc_arr[i]
        t = desc['type']
        attrib=desc['attrib']
        if(t == 'dollar'):
            rslt = rslt + attrib
        elif(t == 'match'):
            rslt = rslt + match
        elif(t == 'left'):
            rslt = rslt + left
        elif(t == 'right'):
            rslt = rslt + right
        elif(t == 'num'):
            rslt = rslt + groups[attrib]
        else:
            rslt = rslt + attrib
    return(rslt)

def replace(s,sub,newsub):
    '''
        s = 'aaBBaaBB'
        replace(s,'aa','AA')
        
        s = '678abc12345uvw444tail333'
        regex = re.compile('[0-9]+')
        replace(s,regex,'AA')
        
        
        def replacer(*args):
            match= args[0] 
            p1=args[1] 
            p2=args[2] 
            p3=args[3]
            offset=args[-2]
            s=args[-1]
            return(elel.join([p1,p2,p3],'-'))
        
        s = '^^^abc12345#$*%tail'
        regex = re.compile("([a-z]+)(\d*)([^\w]*)")
        replace(s,regex,replacer)
        
        #refer to https://developer.mozilla.org/zh-CN/docs/Web/JavaScript/Reference/Global_Objects/String/replace
        #for params
        #$$  '$'
        #$&  match
        #$`  left
        #$'  right
        #$n  groups(n)
        ####
        s = '^^^abc12345#$*%tail'
        regex = re.compile("([a-z]+)(\d*)([^\w]*)")
        m = regex.search(s)
        match = m.group(0)
        match
        left = s[:m.start()]
        left
        right = s[m.end():]
        right
        groups = m.groups()
        groups
        offset = m.start()
        offset
        ####
        params = "@@$$@@$&@@$`@@$'@@$1"
        s = '^^^abc12345#$*%tail'
        regex = re.compile("([a-z]+)(\d+)([^\w]+)")
        replace(s,regex,params)
        
    '''
    t1 = type(sub)
    tr = type(re.compile(""))
    cond1 = (t1 == tr)
    t2 = type(newsub)
    tf = type(lambda x:x)
    cond2 = (t2 == tf)
    if(cond1):
        regex = sub
    else:
        regex = re.compile(re.escape(sub))
    m = regex.search(s)
    ####
    if(m == None):
        return(s)
    else:
        pass
    ####
    match = m.group(0)
    left = s[:m.start()]
    right = s[m.end():]
    groups = list(m.groups())
    offset = m.start()
    if(cond2):
        #match, p1, p2, p3,......., offset,s
        args = [match]
        args.extend(groups)
        args.append(offset)
        args.append(s)
        rslt = newsub(*args)
    else:
        newsub = replace_creat_newsub(newsub,match,groups,left,right)
        rslt = re.sub(regex,newsub,s)
    return(rslt)

def slice(s,si,ei=None,**kwargs):
    '''
        # in python , the string-length means  unicode-char-lngth 
        # in javascript, the length means how-many 16-bit unit
        # for example:
        # run in js 
        bs = b'\xd85\xdcRO`N\xecY}\xd85\xdcR'
        s = bs.decode('utf_16_be')        
        s        
        bytstrm2us(bs,style='js')
        slice(s,0,1,style='py')
        slice(s,0,2,style='py')
        slice(s,0,3,style='py')
        slice(s,0,4,style='py')
        #
        slice(s,0,1,style='js')
        slice(s,0,2,style='js')
        slice(s,0,3,style='js')
        slice(s,0,4,style='js')
        slice(s,0,5,style='js')
        slice(s,0,6,style='js')
        slice(s,0,7,style='js')
    '''
    lngth = length(s,**kwargs)
    if('style' in kwargs):
        style = kwargs['style']
    else:
        style = 'py'
    if(ei == None):
        ei = lngth
    else:
        pass
    si = elel.uniform_index(si,lngth)
    ei = elel.uniform_index(ei,lngth)
    if(style == 'py'):
        part = s[si:ei]
        return(part)
    else:
        locs = str_code_points(s,encode='utf_16_be')
        locs = elel.array_map(locs,lambda ele:ele//2)
        us = str2us(s,encode = 'utf_16_be')
        uarr = us2uarr(us,mode='both')
        jscharr = uarr2jscharr(uarr)
        slb = elel.lower_bound(locs,si)
        sub = elel.upper_bound(locs,si)
        elb = elel.lower_bound(locs,ei)
        eub = elel.upper_bound(locs,ei)
        part1 = jscharr[si:sub]
        s1 = elel.join(part1,'')
        part2 = uarr[sub:elb]
        s2 = uarr2str(part2,style='js')
        part3 = jscharr[elb:ei]
        s3 = elel.join(part3,'')
        s = s1 + s2 + s3
        return(s)


#@@@




def split(s,sp="",limit=None):
    '''
        regex=re.compile("[0-9]+")
        s = 'A111B222CC33D4EEE56789F000A'
        split(s,regex)
        
        regex=re.compile("[0-9]+")
        s = '000A111B222CC33D4EEE56789F000'
        split(s,regex)
        
        
        s = '111A111B111CC111D111'
        split(s,'111')

        s = 'A111B111CC111D'
        split(s,'111')
        
        
        s = 'ABCD'
        split(s)
    '''
    t1 = type(sp)
    tr = type(re.compile(""))
    cond1 = (t1 == tr)
    if(cond1):
        regex = sp
    else:
        regex = re.compile(re.escape(sp))
    it = regex.finditer(s)
    spans = []
    for m in it:
        spans.append(m.span())
    reserved = elel.rangize_supplement(spans,s.__len__())
    def cond_func(ele,s):
        return(slice(s,*ele))
    arr = elel.array_map(reserved,cond_func,s)
    if(spans[0][0] == 0):
        arr = elel.prepend(arr,'')
    else:
        pass
    if((sp == '')|(sp == re.compile(""))):
        arr.pop(0)
        arr.pop(-1)
    else:
        pass
    if(limit == None):
        return(arr)
    else:
        return(arr[:limit])

def startsWith(s,prefix,start=0,end=None):
    '''
    '''
    if(start == None):
        start = s.__len__()
    else:
        pass
    return(str.startswith(s,prefix,start,end))

def substr(s,start,lngth=None,**kwargs):
    if(lngth==None):
        lngth = s.__len__()
    else:
        pass
    return(slice(s,start,start+lngth,**kwargs))

def substring(s,si,ei=None,**kwargs):
    '''
        # refer to https://developer.mozilla.org/zh-CN/docs/Web/JavaScript/Reference/Global_Objects/String/substring
        # substring 提取从 indexStart 到 indexEnd（不包括）之间的字符。特别地：
        
        # 如果 indexStart 等于 indexEnd，substring 返回一个空字符串。
        # 如果省略 indexEnd，substring 提取字符一直到字符串末尾。
        # 如果任一参数小于 0 或为 NaN，则被当作 0。
        # 如果任一参数大于 stringName.length，则被当作 stringName.length。
        # 如果 indexStart 大于 indexEnd，则 substring 的执行效果就像两个参数调换了一样。
        # 例如，str.substring(1, 0) == str.substring(0, 1)。
        # Special !!!, different behavior from slice when si > ei 
        s = "abcde"
        substring(s,1,3)
        substring(s,3,1)
        
    '''
    if(ei == None):
        ei = s.__len__()
    else:
        pass
    si = elel.uniform_index(si,s.__len__())
    ei = elel.uniform_index(ei,s.__len__())
    if(si>ei):
        return(slice(s,ei,si,**kwargs))
    else:
        return(slice(s,si,ei,**kwargs))

def toLowerCase(s,**kwargs):
    return(str.lower(s))

def toUpperCase(s,**kwargs):
    return(str.upper(s))

# not implemented yet
# String.prototype.localeCompare()
# String.prototype.match()
# String.prototype.normalize()
# String.prototype.search()
# String.prototype.toSource()
# String.prototype.toString()
# String.prototype.toLocaleLowerCase()
# String.prototype.toLocaleUpperCase()
# String.prototype.valueOf()

def trim(s,**kwargs):
    '''
        s = '    \r\n\t\t@ABC@\t\t\t'
        trim(s)
        s = '    \r\n\t\t@ABC@\t\t\t'
        trim(s,spaces='\r\n\t@ ')
    '''
    if('spaces' in kwargs):
        spaces = kwargs['spaces']
    else:
        spaces = '\r\n\t\x20'
    s = s.strip(spaces)
    return(s)

def trimLeft(s,**kwargs):
    '''
        s = '    \r\n\t\t@ABC@\t\t\t'
        trimLeft(s)
        trimLeft(s,spaces='\r\n\t@ ')
    '''
    if('spaces' in kwargs):
        spaces = kwargs['spaces']
    else:
        spaces = '\r\n\t\x20'
    s = s.lstrip(spaces)
    return(s)

def trimRight(s,**kwargs):
    '''
        s = '    \r\n\t\t@ABC@\t\t\t'
        trimRight(s)
        trimRight(s,spaces='\r\n\t@ ')
    '''
    if('spaces' in kwargs):
        spaces = kwargs['spaces']
    else:
        spaces = '\r\n\t\x20'
    s = s.rstrip(spaces)
    return(s)


#############################

def divide(s,interval):
    '''
        s = 'abcdefghi'
        divide(s,3)
        divide(s,2)
        divide(s,4)
    '''
    arr = elel.divide(s,interval)
    return(arr)

def indexesAll(s,c):
    '''
        s = "aBCaDEa"
        indexesAll(s,"a")
    '''
    rslt = []
    for i in range(0,s.__len__()):
        if(s[i]==c):
            rslt.append(i)
        else:
            pass
    return(rslt)

def strip(s,chars,count=None,**kwargs):
    '''
        strip("ABABAAAxyzABB","AB")
        strip("ABABAAAxyzABB","AB",2)
        
        strip("ABABAAAxyzABB","AB",mode='whole')
        strip("ABABAAAxyzABB","AB",1,mode='whole')
        strip("ABABAAAxyzABB","AB",2,mode='whole')
    '''
    s = lstrip(s,chars,count,**kwargs)
    s = rstrip(s,chars,count,**kwargs)
    return(s)

def lstrip(s,chars,count=None,**kwargs):
    '''
        lstrip('sssa','s',0)
        lstrip('sssa','s',1)
        lstrip('sssa','s',2)
        lstrip('sssa','s',3)
        lstrip('sssa','s',4)

        lstrip('sbsa','sb',0)
        lstrip('sbsa','sb',1)
        lstrip('sbsa','sb',2)
        lstrip('sbsa','sb',3)
        lstrip('sbsa','sb',4)
        
        lstrip('sbsa','sb',0, mode='whole')
        lstrip('sbsbsa','sb',1, mode='whole')
        lstrip('sbsbsa','sb',2, mode='whole')
        
    '''
    if(count==None):
        count = s.__len__()
    else:
        pass
    if('mode' in kwargs):
        mode = kwargs['mode']
    else:
        mode = 'or'
    if(mode == 'or'):
        c = 0
        for i in range(0,s.__len__()):
            if(c==count):
                break
            else:
                if(s[i] in chars):
                    c = c+1
                else:
                    break
        if(c==0):
            return(s)
        else:
            return(s[c:])
    else:
        step = chars.__len__()
        lngth = s.__len__()
        c = 0
        for i in range(0,lngth,step):
            ele = s[i:i+step]
            cond = (ele == chars)
            if(cond):
                if(c == count):
                    break
                else:
                    c = c + 1
            else:
                break
        if(c == 0):
            return(s)
        else:
            return(s[i:])

def rstrip(s,chars,count=None,**kwargs):
    '''
        rstrip('asss','s',0)
        rstrip('asss','s',1)
        rstrip('asss','s',2)
        rstrip('asss','s',3)
        rstrip('asss','s',4)
        
        rstrip('abbs','sb',0)
        rstrip('abbs','sb',1)
        rstrip('abbs','sb',2)
        rstrip('abbs','sb',3)
        rstrip('abbs','sb',4)
        
        rstrip('asbsbsb','sb',0,mode='whole')
        rstrip('asbsbsb','sb',1,mode='whole')
        rstrip('asbsbsb','sb',2,mode='whole')
        rstrip('asbsbsb','sb',3,mode='whole')
        rstrip('asbsbsb','sb',4,mode='whole')
    '''
    if(count==None):
        count = s.__len__()
    else:
        pass
    if('mode' in kwargs):
        mode = kwargs['mode']
    else:
        mode = 'or'
    if(mode == 'or'):
        c = 0
        for i in range(s.__len__()-1,-1,-1):
            if(c==count):
                break
            else:
                if(s[i] in chars):
                    c = c+1
                else:
                    break
        if(c==0):
            return(s)
        else:
            ei = s.__len__() - c
            return(s[:ei])
    else:
        step = chars.__len__()
        lngth = s.__len__()
        c = 0
        for i in range(lngth-1,-1,-step):
            ele = s[i-step+1:i+1]
            cond = (ele == chars)
            if(cond):
                if(c == count):
                    break
                else:
                    c = c + 1
            else:
                break
        if(c == 0):
            return(s)
        else:
            return(s[:i+1])

def reverse(s):
    '''
        s = 'ABCD'
        reverse(s)
    '''
    arr = list(s)
    arr = elel.reverse(arr)
    s = elel.join(arr,'')
    return(s)

def prepend(s1,s2,count=1):
    '''
        prepend('ABCD','abcd',2)
    '''
    return(s2*count+s1)

def append(s1,s2,count=1):
    '''
        append('ABCD','abcd',2)
    '''
    return(s1+s2*count)

def xor(s1,s2):
    '''
    '''
    S = ""
    for I in range(0,s1.__len__()):
        S += chr(ord(s1[I]) ^ ord(s2[I]));
    return(S)

def tail2head(s, tail_len,**kwargs):
    '''
        tail2head("abcdefghi",0)
        tail2head("abcdefghi",1)
        tail2head("abcdefghi",2)
        tail2head("abcdefghi",3)
        tail2head("abcdefghi",4)
        tail2head("abcdefghi",5)
        tail2head("abcdefghi",6)
        tail2head("abcdefghi",7)
        tail2head("abcdefghi",8)
        tail2head("abcdefghi",9)
        tail2head("abcdefghi",10)
        tail2head("abcdefghi",10,repeat=False)
        tail2head("abcdefghi",11,repeat=False,padding=' ')
        tail2head("abcdefghi",12,repeat=False,padding='@')
        tail2head("abcdefghi",10,repeat=True)
        tail2head("abcdefghi",11,repeat=True)
        tail2head("abcdefghi",12,repeat=True)
    '''
    if("repeat" in kwargs):
        repeat = kwargs['repeat']
    else:
        repeat = True
    if("padding" in kwargs):
        padding = kwargs['padding']
    else:
        padding = '\x00'
    I = ""
    if(repeat):
        for J in range(0,s.__len__()):
            seq = (J + s.__len__() - tail_len) % s.__len__()
            I = I + s[seq]
    else:
        for J in range(0,s.__len__()):
            seq = (J + s.__len__() - tail_len)
            if(seq < 0):
                I = I + padding
            else:
                seq = seq % s.__len__()
                I = I + s[seq]
    return(I)

end2begin = tail2head

def head2tail(s, head_len,**kwargs):
    '''
        head2tail("abcdefghi",0)
        head2tail("abcdefghi",1)
        head2tail("abcdefghi",2)
        head2tail("abcdefghi",3)
        head2tail("abcdefghi",4)
        head2tail("abcdefghi",5)
        head2tail("abcdefghi",6)
        head2tail("abcdefghi",7)
        head2tail("abcdefghi",8)
        head2tail("abcdefghi",9)
        head2tail("abcdefghi",10)
        head2tail("abcdefghi",10,repeat=False)
        head2tail("abcdefghi",11,repeat=False,padding=' ')
        head2tail("abcdefghi",12,repeat=False,padding='@')
        head2tail("abcdefghi",10,repeat=True)
        head2tail("abcdefghi",11,repeat=True)
        head2tail("abcdefghi",12,repeat=True)
    '''
    if("repeat" in kwargs):
        repeat = kwargs['repeat']
    else:
        repeat = 1
    if("padding" in kwargs):
        padding = kwargs['padding']
    else:
        padding = '\x00'
    rslt =tail2head(s, s.__len__() - head_len,repeat=repeat,padding=padding)
    if(repeat):
        pass
    else:
        if(s.__len__() < head_len):
            r = head_len % s.__len__()
            rslt = rslt[:s.__len__()-r] + padding * r
        else:
            pass
    return(rslt)

begin2end = head2tail

def display_width(s):
    '''
        display_width('a')
        display_width('去')
    '''
    s= str(s)
    width = 0
    len = s.__len__()
    for i in range(0,len):
        sublen = s[i].encode().__len__()
        sublen = int(sublen/2 + 1/2)
        width = width + sublen
    return(width)

def prepend_basedon_displaywidth(s,width,**kwargs):
    '''
        prepend_basedon_displaywidth('a',4,padding='x')
        prepend_basedon_displaywidth('去',4,padding='x')
    '''
    if('padding' in kwargs):
        padding = kwargs['padding']
    else:
        padding = ' '
    s = str(s)
    w = display_width(s)
    space_Len = width - w
    new_S = ''
    for i in range(0,space_Len):
        new_S = ''.join((padding, new_S))
    new_S = ''.join((new_S,s))
    return(new_S)

def append_basedon_displaywidth(s,width,**kwargs):
    '''
        append_basedon_displaywidth('a',4,padding='x')
        append_basedon_displaywidth('去',4,padding='x')
    '''
    if('padding' in kwargs):
        padding = kwargs['padding']
    else:
        padding = ' '
    s = str(s)
    w = display_width(s)
    space_Len = width - w
    new_S = padding * space_Len
    new_S = ''.join((new_S,s))
    return(new_S)


def get_substr_arr_via_spans(s,spans):
    new_spans = elel.rangize_fullfill(spans,s.__len__())
    arr = elel.array_map(new_spans,lambda ele:s[ele[0]:ele[1]])
    return(arr)

def search_gen(regex,s,*args):
    args = list(args)
    arrlen = args.__len__()
    if(arrlen==0):
        start = 0
        end = s.__len__()
    elif(arrlen==1):
        start = args[0]
        end = s.__len__()
    else:
        start = args[0]
        end = args[1]
    cur = start
    while(True):
        m = regex.search(s,cur)
        if(m):
            if(m.start()<end):
                cur = m.end()
            else:
                pass
            yield(m)
        else:
            return(None)



def find_all_spans(regex,s):
    rslt = []
    g = search_gen(regex,s)
    for each in g:
        ele = (each.start(),each.end())
        rslt.append(ele)
    return(rslt)


def regex_divide(regex,s):
    spans = find_all_spans(regex,s)
    return(get_substr_arr_via_spans(s,spans))




######

def str2io(s,codec="utf-8"):
    '''
        ugly, because for "io.StringIO" and "io.BytesIO" <io.UnsupportedOperation: fileno>
        so ugly implementation  for giving  string a fileno
    '''
    master_fd, slave_fd = pty.openpty()
    os.write(slave_fd,s.encode(codec))
    return((master_fd, slave_fd))


#####


##C C++ std::string APIs

##lisp APIs

##C#   APIs

##perl APIs

##other languages.....


######code tool

def cap_init(s):
    if(s==""):
        return(s)
    else:
        return(s[0].upper()+s[1:])


def camel2lod(camel):
    rslt = []
    cache = ""
    for i in range(len(camel)):
        c = camel[i]
        if(str.isupper(c)):
            rslt.append(cache.lower())
            cache = c
        else:
            cache = cache + c
    s = ''
    for i in range(0,len(rslt)):
        s = s + rslt[i] + "_"
    if(cache == ""):
        return(s[:-1])
    else:
        return(s + cache.lower())

def lod2camel(lod):
    arr = lod.split("_")
    arr[0] = arr[0].lower()
    for i in range(1,len(arr)):
        arr[i] = cap_init(arr[i])
    s = ''
    for i in range(0,len(arr)):
        s = s + arr[i]
    return(s)

def camel2dash(camel):
    lod = camel2lod(camel)
    return(lod2dash(lod))

def dash2camel(dash):
    lod = dash.replace("-","_")
    return(lod2camel(lod))

def lod2dash(lod):
    return(lod.replace("_","-"))

def dash2lod(dash):
    return(dash.replace("-","_"))

##is_xxxx###

def is_int_str(s):
    n = None
    try:
        n = int(s)
    except:
        return(False)
    else:
        return(str(n) == s)


def is_float_str(s):
    n = None
    try:
        n = float(s)
    except:
        return(False)
    else:
        return(str(n) == s)


#####

##bytes###
##V + ~[keep bitorder]  + O
##S + V + Od + <to> + Oi
#[] 从句
# @ 时间   <>
# # 地点   <>
# $ 时态   <>
# % 目的   <>杀死它  死就是目的
# ~ 方式   <via>

def reverse_four_bytes_keeping_bitorder(L):
    ''' 255       0x00ff
        65280     0xff00
        byte4-byte3-byte2-byte1
        byte1-byte2-byte3-byte4
    '''
    L = (L & 255) << 24 | (L & 65280) << 8 | L >> 8 & 65280 | L >> 24 & 255
    return(L)
