###############################
### ONE TIME PAD | ONE TIME KEY
### very secure if done properly:
### ISSUES:  Crypto 101, page 29
###   * RandomKey needs to be as long as Text (huge problem)
###   * Keys need to be securely exchanged and only used ONCE
###############################

# https://cryptography.fandom.com/wiki/One-time_pad

from bestia.iterate import iterable_to_string

ALPHABET = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'


class OneTimePad(object):

    def __init__(self, key):
        self.key = key

    def __codec(self, txt, mode):

        ''' txt can be either :
                * plain__text for encryption
                * cypher_text for decryption    
        '''

        # each txt_chr needs to be enc|dec with another key_chr, thus ...
        if len(self.key) < len(txt):
            raise Exception('Key CANNOT be shorter than Text')

        blob = []
        for n in range( len(txt) ):

            txt_n = Alpha(txt[n])
            key_n = Alpha(self.key[n])

            if mode == 'ENC':
                ct_n = self.__enc(txt_n, key_n, len(ALPHABET))
            elif mode == 'DEC':
                ct_n = self.__dec(txt_n, key_n, len(ALPHABET))

            blob.append(
                ALPHABET[ct_n]
            )

        return iterable_to_string(blob)

    def __enc(self, t, k, l):
        return ( t + k ) % l

    def __dec(self, t, k, l):
        return ( t - k + l ) % l

    # PUBLIC METHODS
    def encrypt(self, txt):
        return self.__codec(txt, mode='ENC')

    def decrypt(self, txt):
        return self.__codec(txt, mode='DEC')


def Alpha(c):
    return ALPHABET.index(c.upper())
