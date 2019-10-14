import os
import sys
import pickle
from collections import Counter

def get_file_content(filename, check_non_ascii=False):
    content = ''

    with open(filename) as f:
        for line in f:
            content+=line

    # remove all non ascii chars
    filtered = ''.join(
        [i if ord(i) < 128 else ' ' for i in content]
    )

    if check_non_ascii:
        there_is_lost_data(content, filtered)
    
    return filtered

def there_is_lost_data(content, filtered):
    """
    This function reads a file and removes all non ascii characters. 
    If any non-ascii characters are found, warns the user that all non-ascii 
    characters will be lost and if compression should continue
    """

    if content == filtered:
        return
    
    valid = {
        'yes': True,
        'ye': True,
        'y': True,
    }

    sys.stdout.write(
        'This file contains non ascii characters.\nCompressing this file ' +
        'will result in the loss of these characters.\nDo you wish to ' + 
        'continue? [y/N] '
    )

    user_answer = input().lower()

    if not user_answer in valid:
        print('Compression canceled')
        sys.exit()

def get_alphabet(filename, check_non_ascii=False):
    """
    This function returns a dictionary containing 
    the histogram of occurrences of a file.

    This dictionary also has the keys 1 and 0, 
    that will abstract a hoffman tree
    """

    content = get_file_content(filename, check_non_ascii)
    
    char_histogram = Counter(content)

    def format_dict(k, v):
        retn = {}
        retn['probability'], retn['value'] = v, k
        retn[0], retn[1] = None, None
        return retn

    char_histogram = { k: format_dict(k, v) for k,v in char_histogram.items() }

    return char_histogram

def huffman_tree(alphabet):
    while len(alphabet) > 1:
        sorted_alphabet = sorted(alphabet, key=lambda x: alphabet[x]['probability'])

        new_symbol_name = '{0}{1}'.format(
            alphabet[sorted_alphabet[0]]['value'], alphabet[sorted_alphabet[1]]['value']
        )

        new_node = {
            'probability': alphabet[sorted_alphabet[0]]['probability'] + alphabet[sorted_alphabet[1]]['probability'],
            0: alphabet[sorted_alphabet[0]],
            1: alphabet[sorted_alphabet[1]],
            'value': new_symbol_name
        }

        alphabet[new_node['value']] = new_node
        del alphabet[sorted_alphabet[0]]
        del alphabet[sorted_alphabet[1]]

    root = [*alphabet][0]

    return alphabet[root]

def padding_cipher(ciphered):
    extra_padding = 8 - len(ciphered) % 8

    for i in range(extra_padding):
        ciphered += '0'
    
    padded_info = "{0:08b}".format(extra_padding)

    # the first 1 byte says how many zeros was added
    ciphered = padded_info + ciphered

    return ciphered

def remove_padding(padded_cipher):
    padded_info = padded_cipher[:8]
    extra_padding = int(padded_info, 2)

    padded_cipher = padded_cipher[8:]
    cipher = padded_cipher[:-1*extra_padding]
    
    return cipher

def get_byte_array(padded_cipher):
    byte_array = bytearray()

    for i in range(0, len(padded_cipher), 8):
        byte = padded_cipher[i: i+8]
        byte = int(byte, 2)
        byte_array.append(byte)
    
    return byte_array

def save_huffman_tree(huffman_tree, filename):
    pickle.dump(huffman_tree, open(filename, 'wb'))

def save_ciphered_file(ciphered, filename):
    with open(filename, 'wb') as file:
        padded_cipher = padding_cipher(ciphered)
        byte_array = get_byte_array(padded_cipher)
        file.write(bytes(byte_array))

def load_huffman_tree(filename):
    huffman_tree = pickle.load(open(filename, 'rb'))
    return huffman_tree

def save_file_content(deciphered_text, filename):
    with open(filename, "w") as file:
        file.write(deciphered_text)

def load_ciphered_file(filename):
    with open(filename, 'rb') as file:
        padded_cipher = ""
        
        byte = file.read(1)
        while(byte != b''):
            byte = ord(byte)
            bits = bin(byte)[2:].rjust(8, '0')
            padded_cipher += bits
            byte = file.read(1)
        
        ciphered = remove_padding(padded_cipher)
    
    return ciphered

def huffman_cipher(text, huffman_tree):
    ciphered = ''

    for ch in text:
        current_branch = huffman_tree
        while True:
            if current_branch[0] is None and current_branch[1] is None:
                break

            if ch in current_branch[0]['value']:
                ciphered += '0'
                current_branch = current_branch[0]
            else:
                ciphered += '1'
                current_branch = current_branch[1]

    return ciphered

def huffman_decipher(ciphered, huffman_tree):
    
    plain_text = ''
    current_branch = huffman_tree

    for ch in ciphered:
        if current_branch[0] is None and current_branch[1] is None:
            plain_text += current_branch['value']
            current_branch = huffman_tree
        
        current_branch = current_branch[int(ch)]

    plain_text += current_branch['value']

    return plain_text

def compression_ratio(FILENAME, zipped_file, decode_tree):

    orig_size = os.stat(FILENAME).st_size
    huff_size = os.stat(zipped_file).st_size

    ratio = huff_size / orig_size
    ratio = round(ratio*100, 2)
    
    return ratio

def get_directory_reference(CIPHERFILE):
    path = CIPHERFILE.split('/')
    filename, path[-1] = path[-1], ''
    path = '/'.join(path)
    filename = path + filename + '.txt'
    return filename