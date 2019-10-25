# https://en.wikipedia.org/wiki/RSA_(cryptosystem)
# https://simple.wikipedia.org/wiki/RSA_algorithm
# https://pastebin.com/u/RootOfTheNull

# http://factordb.com/index.php?id=
# https://www.alpertron.com.ar/ECM.HTM

from bestia.output import echo

from Crypto.PublicKey import RSA
from Crypto.Util import number
# pip3 uninstall crypto
# pip3 install pycrypto

# import gmpy2
import math

class FailedPhiCalc(Exception):
    pass

class NotPrime(Exception):
    pass

# i think the idea behind breaking rsa is that
# u can still get enough info out of a public_key, 
# (N, to factorize p*q - small E for cuberoot attack)
# and from there get private_key OR decrypt etc...


def is_prime(n):
    # primes always POSITIVE
    if n > 1:
        for i in range(2, n):
            if (n % i) == 0:
                return
        return True


def product_of(*ints):
    r = 1
    for i in ints: 
        r = r * i
    return r  


def are_coprimes(x, y):
    ''' tests if greatest common divisor is 1 '''
    gcd = math.gcd(x, y)
    # input(gcd)
    return gcd  == 1



def square_root(n):

    # return int(math.sqrt(n)) # OverflowError: int too large to convert to float
    # return gmpy2.isqrt(n)    # ImportError: ....

    x = n
    y = (x + n // x) // 2
    while y < x:
        x = y
        y = (x + n // x) // 2
    return x


def cube_root(x):
    y, y1 = None, 2
    
    while y!=y1:
        y = y1
        y3 = y**3
        d = (2*y3+x)
        y1 = (y*(y3+2*x)+d//2)//d
    
    return y 


def fermat_factorize(n):
    # Source - http://stackoverflow.com/a/20465181

    a = square_root(n)
    b = square_root(n)
    b2 = a*a - n
    # b = square_root(n)

    count = 0
    while b*b != b2:
        a = a + 1
        b2 = a*a - n
        b = square_root(b2)
        echo(b, 'red')
        input()
        count += 1

    p = a+b
    q = a-b
    assert n == p * q
    return p, q



class Rsa(object):

    def __init__(self, factors=[], n=0x0, e=0x10001):

        ##################
        ### PUBLIC KEY ###
        ##################

        # [e]ncryption exponent
        self.e = e

        # modulus
        self.n = n # cannot be 0 ...

        # n FACTORS ARE NOT Always needed...
        # MUST be primes, preferably LARGE
        self.factors = [
            # allow MULTI-PRIME key
            # p, q,
            *factors
        ]


        ###################
        ### PRIVATE KEY ###
        ###################

        # [d]ecryption exponent
        self.d = 0   # modular inverse


        #################
        ### ARTIFACTS ###
        #################

        # message, plain_text
        self.m = 0

        # cypher_text
        self.c = 0


    @property
    def n(self):
        if not self.__n:
            # print('calculating n = p * q ...')
            self.__n = self.factors[0] * self.factors[1]

        return self.__n

    @n.setter
    def n(self, n):
        self.__n = int(n)



    @property
    def phi(self):
        ''' AKA totient,
        MUST be coprime with e (share no common factors other than 1)
        https://www.mathsisfun.com/definitions/coprime.html
        '''

        if not self.factors:
            if self.n:
                # attempt to factorize N
                input('Factorize N in factordb')
            else:
                raise FailedPhiCalc('Missing n, p, q to calculate Totient')


        if len(self.factors) > 1:
            totient = int(
                product_of( *[ f -1 for f in self.factors ] )
            )

        else:
            # if ONLY 1 factor
            if self.n:
                p = self.factors[0]
                q = int(self.n / self.factors[0])
                totient = int(
                   ( p - 1 ) * ( q - 1 )
                )
            else:
                raise FailedPhiCalc('Missing n to calculate Totient')


        if self.e:
            if not are_coprimes(self.e, totient):
                raise FailedPhiCalc('Totient is not co-prime with E')

        return totient



    @property
    def d(self):
        # https://gist.github.com/ofaurax/6103869014c246f962ab30a513fb5b49
        # return self.e ** (0 - 1) % self.phi
        return number.inverse(self.e, self.phi)


    @d.setter
    def d(self, d):
        self.__d = int(d)



    def encrypt(self, p):
        ''' using ct ** d gets stuck for large numbers,
        pow() solves the issue '''
        self.c = pow(p, self.e, self.n)
        _ = self.c
        self.c = 0
        return _


    def decrypt(self, c, decode=''):

        if self.e == 3:
            echo('Trying cube-root attack...', 'red')
            self.m = cube_root(c)

        else:
            #  using ct ** d gets stuck for large numbers, pow() solves issue
            self.m = pow(c, self.d, self.n) # int

        if decode:
            self.m = num_to_txt(self.m, codec=decode)

        _ = self.m
        self.m = 0
        return _


def num_to_txt(num, codec='utf-8'):
    hex_string = hex(num).lstrip('0x').rstrip('L')
    str_bytes = bytes.fromhex(hex_string)    # bytes
    txt = str_bytes.decode(codec)            # str
    return txt


def txt_to_num(txt, codec='utf-8'):
    str_bytes = bytes(txt, codec)    # encode into bytes
    hex_string = str_bytes.hex()     # hex_string
    num = int(hex_string, 16)        # number
    return num

