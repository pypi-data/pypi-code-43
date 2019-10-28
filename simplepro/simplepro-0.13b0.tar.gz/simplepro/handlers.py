import os #line:1
import struct #line:2
import rsa #line:3
so_file =open (os .path .join (os .path .dirname (__file__ ),'simplepro.so'),'rb')#line:6
buffer =so_file .read (2 )#line:7
r ,=struct .unpack ('h',buffer )#line:8
buffer =so_file .read (r )#line:9
pri =buffer #line:10
strs =bytearray ()#line:12
while True :#line:13
    temp =so_file .read (4 )#line:14
    if len (temp )==0 :#line:15
        so_file .close ()#line:16
        break #line:17
    size ,=struct .unpack ('i',temp )#line:18
    d =so_file .read (size )#line:19
    privkey =rsa .PrivateKey .load_pkcs1 (pri )#line:20
    strs .extend (rsa .decrypt (d ,privkey ))#line:21
exec (compile (strs .decode (encoding ='utf8'),'<string>','exec'))#line:22
def process_request (request ,path ):#line:25
    if path .endswith ('simplepro/active/'):#line:26
        return process_lic (request )#line:27
    elif path .endswith ('simplepro/info/'):#line:28
        return process_info (request )#line:29
def process_view (request ,view ):#line:32
    return pre_process (request ,view )#line:33
