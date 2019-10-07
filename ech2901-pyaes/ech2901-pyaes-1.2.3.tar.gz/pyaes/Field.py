# itertools functions only used in __mul__ function currently

# TODO remake inverse property of GF class so it isn't a brute force approach


class GF(object):
    def __init__(self, val: int):
        """
        Galois(Finite) Field class that does most of the math behind the scenes

        :param val: int
        """

        if type(val) != int:
            raise TypeError(f'Expected <int> input and received a {type(val)}')
        elif val < 0:
            raise ValueError(f'Expected positive integer and recieved {val}')

        self.int = val


    @property
    def inverse(self):
        """
        Brute force finding the inverse
        of a given Galois Field value.


        :return: GF
        """

        if self.int == 0:
            # 0 has no inverse, so return itself
            return self
        if self.int == 1:
            # Inverse of 1 is 1
            return self

        # Honestly, this is a brute force approach to finding an inverse.
        # Will replace later with a better solution
        for i in range(2, 256):
            out = GF(i)
            if self.mul(out, modulus).int == 1:
                return out

    def __mul__(self, other):
        """
        Multiply two GF objects together
        Does not maintain finite field.

        :param other: GF
        :return: GF
        """
        if type(other) != type(self):
            # Make sure that we're only operating on GF objects
            raise TypeError(f'Expected <GF> input and received a {type(other)}')

        if self.int == 0 or other.int == 1:
            # Anything times 0 is zero
            # Anything times 1 is the value
            return self
        if other.int == 0 or self.int == 1:
            # Anything times 0 is zero
            # Anything times 1 is the value
            return other

        # Can not be simple multiplication as
        # some will not correctly accumulate value
        # IE: GF(14) * GF(112) == GF(1568)
        # however, 14 * 112 == 672

        out = 0  # Placeholder for the output
        test_val = 1  # So we don't keep recalculating things as much
        for i in range(other.int.bit_length()):
            if other.int & test_val:
                out = out ^ self.int << i

            test_val = test_val << 1

        return GF(out)

    def __xor__(self, other):
        """
        xor the values of two GF objects

        :param other: GF
        :return: GF
        """
        # Just the xoring of two ints
        return GF(self.int ^ other.int)

    def __floordiv__(self, other):
        """
        calculate the quotient of two GF objects

        :param other: GF
        :return: GF
        """
        if type(other) != type(self) and type(self) == GF:
            # Make sure we're working on GF objects
            raise TypeError

        if self.int == 0:
            # 0 divided anything is zero
            return self
        if other.int == 0:
            # Technically I should raise a ZeroDivisionError but I don't know how that'll go yet
            return other

        max1 = self.int.bit_length()
        max2 = other.int.bit_length()

        temp = self.int
        out = 0

        while temp.bit_length() >= other.int.bit_length():

            out = out | 1 << (max1 - max2)
            temp = temp ^ (other.int << (max1 - max2))
            max1 = temp.bit_length()

        return GF(out)

    def __mod__(self, other):
        """
        calculate the modulus of two GF objects

        :param other: GF
        :return: GF
        """
        if type(other) != type(self) and type(self) == GF:
            # Make sure we're working on GF objects
            raise TypeError

        if self.int == 0:
            # 0 modulus anything is zero
            return self
        if other.int == 0:
            # Technically I should raise a ZeroDivisionError but I don't know how that'll go yet
            return other

        max1 = self.int.bit_length()
        max2 = other.int.bit_length()

        out = self.int

        while out.bit_length() >= other.int.bit_length():

            out = out ^ (other.int << (max1 - max2))
            max1 = out.bit_length()

        return GF(out)


    def __str__(self):
        """
        return hex representation of the int property

        different from the hex property as this has no
        leading '0x' characters and is justified to the right
        so that there is a leading '0' when appropriate for a
        single byte.

        :return: str
        """
        return hex(self.int)[2:].rjust(2, "0")

    def __eq__(self, other):
        """
        Test equality of two GF objects

        :param other: GF
        :return: bool
        """
        if type(other) != GF:
            return False
        return self.int == other.int

    def mul(self, other, modulus):
        """
        Return the product of two GF objects modulus another GF object

        :param other: GF
        :param modulus: GF
        :return: GF
        """

        return (self * other) % modulus

    def __repr__(self):
        return f'{self.int}'


def sbox(gf):
    """
    Calculate the Rjindael S-Box of a GF object

    :param gf: GF
    :return: GF
    """

    # Using the inverse of the given GF object
    val = gf.inverse.int
    out = val ^ 0x63

    for i in range(1, 5):
        # repeatedly shift the bits to the left and xor with output
        out = out ^ (((val << i) & 0xff) | (val >> (8 - i)))

    return GF(out)


def invsbox(gf):
    """
    Calculate the Rjindael Inverse S-Box of a GF object

    :param gf: GF
    :return: GF
    """

    val = gf.int
    out = 0x5

    # repeatedly shift the bits to the left and xor with output
    for i in [1, 3, 6]:
        out = out ^ (((val << i) & 0xff) | (val >> (8 - i)))

    # Return the inverse of the calculated GF object
    return GF(out).inverse


modulus = GF(283)
