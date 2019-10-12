name='core'

from .utils import *

def compress(FILENAME):
    alphabet = utils.get_alphabet(FILENAME)

    huffman_tree = utils.huffman_tree(alphabet)

    plain_text = utils.get_file_content(FILENAME)

    ciphered = utils.huffman_cipher(plain_text, huffman_tree)

    deciphered = utils.huffman_decipher(ciphered, huffman_tree)

    print('Plain Text:', plain_text, end='\n\n')
    print('Ciphered:', ciphered, end='\n\n')
    print('Deciphered:', deciphered, end='\n\n')
    print('Huffman Dict:', huffman_tree, end='\n\n')
