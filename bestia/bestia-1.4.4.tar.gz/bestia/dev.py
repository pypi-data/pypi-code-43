# USE THIS MODULE TO TEST LIBRARY API BEFORE COMMITING/UPLOADING
import os, sys

# DIRECTLY IMPORT SAME DIR MODULES
#   , NOT BESTIA INSTALLED MODULES
from connect import *
from error import *
from iterate import *
from misc import *
from output import *

def flatten_string(string):
    old_char = ''
    new_char = bytearray()
    for c in string:
        b = bytearray(c, ENCODING)
        if sys.getsizeof(c) != CHAR_SIZE:
            old_char += c
            unicode_code_point = ord(c) # int
            new_char.append(unicode_code_point)
    new_char = new_char.decode()
    return string.replace(old_char, new_char)


def flatten_char(c):
    size = sys.getsizeof(c)
    if size != CHAR_SIZE:
        color = 'red'
        symbol = '!='
    else:
        color = 'green'
        symbol = '=='
    echo('{} | size: {} {} {} | utf_code_point: {}'.format(c, size, symbol, CHAR_SIZE, ord(c)), color)


def redecode_unicode_chars(input_string):
    # change replace_special_chars with this
    suspects = [
        'Ã', 
        'Â',
        'Å',
        'Ä',
        # 'Ã®',
    ]
    output_string = ''
    detected = False
    new_char = bytearray()
    for c in input_string:
        size = sys.getsizeof(c)
        # CHAR SIZE IS NOT A GOOD IDICATOR OF WHEN WE WILL FIND
        # if size == CHAR_SIZE and not detected:
        if c not in suspects and not detected:
            echo('standard char: {}'.format(c))
            output_string += c

        elif c in suspects and not detected:
            echo('1 suspect char: {}'.format(c))
            flatten_char(c)
            detected = True
            unicode_code_point = ord(c) # int
            new_char.append(unicode_code_point)

        elif size != CHAR_SIZE and detected:
            echo('2 suspect char: {}'.format(c))
            flatten_char(c)
            unicode_code_point = ord(c) # int
            new_char.append(unicode_code_point)

            detected = False
            output_string += new_char.decode(ENCODING)
            new_char = bytearray()
            # this assumes that I will be encoding chars in chunks of length 2... is that fair ????

        # echo(output_string)
    return output_string

if __name__ == "__main__":

    # asd = '\033[4mYO\033[0m'
    # for c in asd:
    #     if c == '\\':
    #         input(c)
    # print(asd)
    # print(asd.strip('\033[0m'))

    FString(
        'ABC', 
        fg='red', 
        bg='blue',
        fx=[
            # 'bold',
            # 'faint',
            'underline',
            'blink',

            'reverse',
            # 'conceal',

            # 'cross',

            # 'frame',
            # 'circle',
            # 'overline',

        ],
        size=7,
        align='c',
        # pad='*',
    ).echo()

    exit()

    # print(expand_seconds(1234567890))
    # print(expand_seconds(1890, output_string=1))

    d = {
        'a': 1,
        'a2': {
            'b5': 29,
            'b2': 25,
            'bp': 2,
        },
        'a3': 1,
        'a4': 1,
        'a5': 1,
        'a6': 1,
        'a7': 1,
    }


    # Dumbo DVDRip [dublat romana]
    # zburător
    # cunoştinţă
    # descoperă
    rumeno = '''Faceãi cunostinãÄƒ cu Dumbo, puiul cel mititel ÅŸi dulce al Doamnei Jumbo, care Ã®i farmecÄƒ pe to
    ãi cei care Ã®l vÄƒd... pânÄƒ când lumea descoperÄƒ cÄƒ are niÅŸte urechi mari ÅŸi clÄƒpÄƒuge.

    Ajutat de cel mai bun prieten al lui, ÅŸoricelul Timothy, Dumbo Ã®ÅŸi dÄƒ seama Ã®n scurtÄƒ vreme cÄ
    ƒ urechile lui spectaculoase Ã®l fac sÄƒ fie un personaj unic, cu totul deosebit, care poate deveni
    celebru Ã®n chip de unic elefant zburÄƒtor al lumii.'''

    # print(replace_special_chars(rumeno))
    # ƒ ord() returns 402 ... out of range
    # Ÿ | size: 76 != 50 | utf_code_point: 376

    # how to separate ú from © ??
    # Å£Äƒ	are these 1 or 2 chars ? surely not 1 ... ?


