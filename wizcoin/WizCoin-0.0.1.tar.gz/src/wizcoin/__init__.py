"""
WizCoin is a class to represent a quantity of coins in a wizard currency.

In this currency, there are knuts, sickles (worth 29 knuts), and galleons
(worth 17 sickles or 493 knuts).
"""

__version__ = '0.0.1'

import copy
import operator

# Constants used in this module:
KNUTS_PER_SICKLE = 29
SICKLES_PER_GALLEON = 17
KNUTS_PER_GALLEON = SICKLES_PER_GALLEON * KNUTS_PER_SICKLE


class WizCoinException(Exception):
    """Exceptions of this class are raised by the wizcoin module for incorrect
    use of the module. If wizcoin is the source of any other raised exceptions,
    assume that it is caused by a bug in the module instead of misuse."""
    pass


class Coins:
    """Coins objects represent an amount of coins, not money. They cannot
    have half a coin, or a negative number of coins."""

    issuer = 'gb' # The ISO 2-letter country code of who issues this currency.



    def __init__(self, initGalleons=0, initSickles=0, initKnuts=0):
        """Create a new Coins object with galleons, sickles, and knuts."""
        self.galleons = initGalleons
        self.sickles  = initSickles
        self.knuts    = initKnuts

        # NOTE: __init__() methods NEVER have a return statement.


    @property
    def galleons(self): # Called when `ob.galleons` property is accessed.
        """The number of galleons in the Coins."""
        return self.__galleons


    @galleons.setter
    def galleons(self, value): # Called on `obj.galleons = 42`
        if not isinstance(value, int) or value < 0:
            raise WizCoinException('galleons attr must be a positive int')
        self.__galleons = value


    @galleons.deleter
    def galleons(self): # Called on `del obj.galleons`.
        self.__galleons = 0


    @property
    def sickles(self):
        """The number of sickles in the Coins."""
        return self.__sickles


    @sickles.setter
    def sickles(self, value):
        if not isinstance(value, int) or value < 0:
            raise WizCoinException('sickles attr must be a positive int')
        self.__sickles = value


    @sickles.deleter
    def sickles(self):
        self.__sickles = 0


    @property
    def knuts(self):
        """The number of knuts in the Coins."""
        return self.__knuts


    @knuts.setter
    def knuts(self, value):
        if not isinstance(value, int) or value < 0:
            raise WizCoinException('knuts attr must be a positive int')
        self.__knuts = value


    @knuts.deleter
    def knuts(self):
        self.__knuts = 0


    @property
    def value(self):
        """The value (in knuts) of all the coins in this Coins object."""
        return (self.__galleons * KNUTS_PER_GALLEON) + (self.__sickles * KNUTS_PER_SICKLE) + (self.__knuts)


    def convertToGalleons(self):
        """Modifies the Coins in-place, converting knuts and sickles to
        galleons. There may knuts and sickles leftover as change."""

        # Convert knuts to sickles, then sickles to galleons.
        self.__sickles += self.__knuts // KNUTS_PER_SICKLE
        self.__knuts %= KNUTS_PER_SICKLE # Knuts may be remaining as change.
        self.__galleons += self.__sickles // SICKLES_PER_GALLEON
        self.__sickles %= SICKLES_PER_GALLEON # Sickles might remain as change.


    def convertToSickles(self):
        """Modifies the Coins object in-place, converting knuts and
        galleons to sickles. There may knuts leftover as change."""
        self.__sickles += (self.__galleons * SICKLES_PER_GALLEON) + (self.__knuts // KNUTS_PER_SICKLE)
        self.__knuts %= KNUTS_PER_SICKLE # Knuts might remain as change.
        self.__galleons = 0


    def convertToKnuts(self):
        """Modifies the Coins object in-place, converting galleons and
        sickles to knuts."""
        self.__knuts += (self.__galleons * KNUTS_PER_GALLEON) + (self.__sickles * KNUTS_PER_SICKLE)
        self.__galleons = 0
        self.__sickles = 0


    def __repr__(self):
        """Returns a string representation of this Coins object that can be
        fed into the interactive shell to make an identical Coins object."""
        className = self.__class__.__qualname__
        return '%s(galleons=%s, sickles=%s, knuts=%s)' % (className, self.__galleons, self.__sickles, self.__knuts)


    def __len__(self):
        """Returns the number of coins in this Coins."""
        return self.__galleons + self.__sickles + self.__knuts


    def __copy__(self):
        """Returns a new, duplicate Coins object of this Coins."""
        return Coins(self.__galleons, self.__sickles, self.__knuts)


    def __deepcopy__(self, memo):
        """Returns a new, duplicate Coins object of this Coins. This
        method reuses __copy__() since Coinss don't need deep copies."""
        return self.__copy__()


    def __str__(self):
        """Returns a string representation of the Coins object, formatted
        like '2g,5s,10k' for a Coins of 2 galleons, 5 sickles, 10 knuts."""
        return '%sg,%ss,%sk' % (self.__galleons, self.__sickles, self.__knuts)


    def __int__(self):
        """Returns the value of the coins in this Coins as an int."""
        return self.value


    def __float__(self):
        """Returns the value of the coins in this Coins as a float."""
        return float(self.value)


    def __bool__(self):
        """Returns the Boolean value of the Coins."""
        return not (self.__galleons == 0 and self.__sickles == 0 and self.__knuts == 0)


    @classmethod
    def fromStr(cls, coinStr):
        """An alternative constructor that gets the coin amounts from
        `coinStr`, which is formatted like '2g,5s,10k'."""
        try:
            if coinStr == '':
                return cls(galleons=0, sickles=0, knuts=0)

            gTotal = 0
            sTotal = 0
            kTotal = 0

            for coinStrPart in coinStr.split(','):
                if coinStrPart.endswith('g'):
                    gTotal += int(coinStrPart[:-1])
                elif coinStrPart.endswith('s'):
                    sTotal += int(coinStrPart[:-1])
                elif coinStrPart.endswith('k'):
                    kTotal += int(coinStrPart[:-1])
                else:
                    raise Exception()
        except:
            raise WizCoinException('coinStr has an invalid format')
        return cls(galleons=gTotal, sickles=sTotal, knuts=kTotal)


    # TODO get rid of this, it doesn't really fit. We'll need another @classmethod example.
    @classmethod
    def isEuropeanCurrency(cls):
        """A helper method that returns if this currency is used in Europe."""
        return cls.issuer in {'ad', 'al', 'am', 'at', 'ba', 'be', 'bg', 'by', 'ch', 'cy', 'cz', 'de', 'dk', 'ee', 'es', 'fi', 'fo', 'fr', 'gb', 'ge', 'gi', 'gr', 'hr', 'hu', 'ie', 'im', 'is', 'it', 'li', 'lt', 'lu', 'lv', 'mc', 'md', 'me', 'mk', 'mt', 'nl', 'no', 'pl', 'po', 'pt', 'ro', 'rs', 'ru', 'se', 'si', 'sk', 'sm', 'tr', 'ua', 'va'}

    # TODO - I'll need an example of a @staticmethod now that _isCoinsType is gone.


    # Overloading comparison operators:
    def _comparisonOperatorHelper(self, operatorFunc, other):
        """A helper method that carries out a comparison operation."""
        if other.__class__ is self.__class__:
            # Compare this Coins's value with another Coins's value.
            return operatorFunc(self.value, other.value)
        elif isinstance(other, (int, float)): # TODO - check if this is correct.
            # Compare this Coins's value with an int or float.
            return operatorFunc(self.value, other)
        # TODO - should we add a way to compare this object with 3-integer tuples (and other sequences)?
        elif operatorFunc == operator.eq:
            return False # Not equal to all non Coins/int/float values.
        elif operatorFunc == operator.ne:
            return True # Not equal to all non Coins/int/float values.
        else:
            # Can't compare with whatever data type `other` is.
            return NotImplemented


    def __eq__(self, other):
        """Overloads the == operator to compare Coins objects with ints,
        floats, and other Coins objects."""
        return self._comparisonOperatorHelper(operator.eq, other)


    def __ne__(self, other):
        """Overloads the != operator to compare Coins objects with ints,
        floats, and other Coins objects."""
        return self._comparisonOperatorHelper(operator.ne, other)


    def __lt__(self, other):
        """Overloads the < operator to compare Coins objects with ints,
        floats, and other Coins objects."""
        return self._comparisonOperatorHelper(operator.lt, other)


    def __le__(self, other):
        """Overloads the <= operator to compare Coins objects with ints,
        floats, and other Coins objects."""
        return self._comparisonOperatorHelper(operator.le, other)


    def __gt__(self, other):
        """Overloads the > operator to compare Coins objects with ints,
        floats, and other Coins objects."""
        return self._comparisonOperatorHelper(operator.gt, other)


    def __ge__(self, other):
        """Overloads the >= operator to compare Coins objects with ints,
        floats, and other Coins objects."""
        return self._comparisonOperatorHelper(operator.ge, other)


    # Overloading math operators:
    def __mul__(self, other):
        """Overloads the * operator to produce a new Coins object with the
        product amount. `other` must be a positive int."""
        if isinstance(other, int) and other >= 0:
            return Coins(self.__galleons * other,
                           self.__sickles * other,
                           self.__knuts * other)
        else:
            return NotImplemented


    def __rmul__(self, other):
        """Overloads the * operator to produce a new Coins object with the
        product amount. `other` must be a positive int."""
        return self.__mul__(other) # * is commutative, reuse __mul__().


    def __imul__(self, other):
        """Overloads the * operator to modify a Coins object in-place with
        the product amount. `other` must be a positive int."""
        if isinstance(other, int) and other >= 0:
            self.__galleons *= other # In-place modification.
            self.__sickles *= other
            self.__knuts *= other
        else:
            return NotImplemented
        return self


    def __add__(self, other):
        """Overloads the + operator to produce a new Coins object with the
        sum amount. `other` must be a Coins."""
        if other.__class__ is self.__class__:
            return Coins(self.__galleons + other.galleons,
                           self.__sickles + other.sickles,
                           self.__knuts + other.knuts)
        else:
            return NotImplemented


    def __iadd__(self, other):
        """Overloads the += operator to modify this Coins in-place with the
        sum amount. `other` must be a Coins."""
        if other.__class__ is self.__class__:
            self.__galleons += other.galleons # In-place modification.
            self.__sickles += other.sickles
            self.__knuts += other.knuts
        else:
            return NotImplemented
        return self


    def __sub__(self, other):
        """Overloads the - operator to produce a new Coins object with the
        difference amount. `other` must be a Coins object with less than or
        equal number of coins of each type as this Coins object."""
        if other.__class__ is self.__class__:
            if self.__galleons < other.galleons or self.__sickles < other.sickles or self.__knuts < other.knuts:
                # Coins objects represent an amount of physical coins, not a
                # monetary value, so there can't be negative coins.
                raise WizCoinException('subtracting %s from %s would result in negative quantity of coins' % (other, self))
            return Coins(self.__galleons - other.galleons,
                           self.__sickles - other.sickles,
                           self.__knuts - other.knuts)
        else:
            return NotImplemented


    def __isub__(self, other):
        """Overloads the -= operator to modify this Coins in-place with the
        difference amount. `other` must be a Coins object with less than or
        equal number of coins of each type as this Coins object."""
        if other.__class__ is self.__class__:
            if self.__galleons < other.galleons or self.__sickles < other.sickles or self.__knuts < other.knuts:
                raise WizCoinException('subtracting %s from %s would result in negative quantity of coins' % (other, self))
            self.__galleons -= other.galleons
            self.__sickles -= other.sickles
            self.__knuts -= other.knuts
        else:
            return NotImplemented
        return self


    def __lshift__(self, other):
        """Overloads the << operator to transfer all coins from the Coins on
        the right side to the Coins on the left side."""
        if other.__class__ is not self.__class__:
            return NotImplemented

        self.__galleons += other.galleons # Add to this Coins.
        self.__sickles += other.sickles
        self.__knuts += other.knuts
        other.galleons = 0 # Empty the other Coins.
        other.sickles = 0
        other.knuts = 0


    def __rshift__(self, other):
        """Overloads the >> operator to transfer all coins from the Coins on
        the left side to the Coins on the right side."""
        if other.__class__ is not self.__class__:
            return NotImplemented

        other.galleons += self.__galleons # Add to the other Coins.
        other.sickles += self.__sickles
        other.knuts += self.__knuts
        self.__galleons = 0 # Empty this Coins.
        self.__sickles = 0
        self.__knuts = 0


    def __getitem__(self, idx):
        """Overloads the [] operator to access what kind of coin is at index
        `idx`. The order of coins is galleons, then sickles, then knutes."""
        if idx >= len(self) or idx < -len(self):
            raise WizCoinException('index out of range')
        if idx < 0:
            idx = len(self) + idx # Convert negative index to positive.

        if idx < self.__galleons:
            return 'galleon'
        elif idx < self.__galleons + self.__sickles:
            return 'sickle'
        else:
            return 'knut'


    def __setitem__(self, idx, coinType):
        """Overloads the [] operator to access what kind of coin is at index
        `idx`. The order of coins is galleons, then sickles, then knutes."""
        if coinType not in ('galleon', 'sickle', 'knut'):
            raise WizCoinException("coinType must be one of 'galleon', 'sickle', or 'knut'")
        try:
            coin = self[idx]
        except Exception as exc:
            raise WizCoinException(str(exc))

        if coin == 'galleon':
            self.__galleons -= 1
        elif coin == 'sickle':
            self.__sickles -= 1
        elif coin == 'knut':
            self.__knuts -= 1

        # Add a coin of type `coinType`.
        if coinType == 'galleon':
            self.__galleons += 1
        elif coinType == 'sickle':
            self.__sickles += 1
        elif coinType == 'knut':
            self.__knuts += 1


    def __delitem__(self, idx):
        """Overloads the [] operator to remove the kind of coin at index
        `idx`."""
        try:
            coin = self[idx]
        except Exception as exc:
            raise WizCoinException(str(exc))

        if coin == 'galleon':
            self.__galleons -= 1
        elif coin == 'sickle':
            self.__sickles -= 1
        elif coin == 'knut':
            self.__knuts -= 1


    def __iter__(self):
        """Returns an iterator that iterates over the coins in this Coins.
        The order of coins is galleons, then sickles, then knuts."""
        return CoinsIterator(self)

    __hash__ = None # TODO - make an immutable version of this class? Do that with inheritance? Or flip the script and make the subclass mutable?


# TODO - can we merge this with CoinsCollection somehow?
class CoinsIterator:
    def __init__(self, CoinsObj):
        """Creates an iterator for the given Coins object."""
        self.nextIndex = 0
        self.CoinsObj = CoinsObj

    def __next__(self):
        """Returns the next coin from the Coins. The order of coins is
        galleons, then sickles, then knuts."""
        if self.nextIndex >= len(self.CoinsObj):
            raise StopIteration

        nextCoin = self.CoinsObj[self.nextIndex]
        self.nextIndex += 1
        return nextCoin

# TODO - maybe I should rename this CoinsSequence? It's not exactly a list of Coins objects, but I'm not sure what unique thing it provides that a list wouldn't, aside from properties.
# TODO - or maybe rename it to BalancedCoinsCollection or BalancedCoinsSequence or BalancedCoins, since the enter/exit is used for ensuring that coins have just been swapped around and not changed.
class CoinsCollection:
    # TODO - this is a sequence, make sure it implements all the sequence stuff. How is this different from a list of coin objects? Because we probide the g/s/k/v properties?
    def __init__(self, allCoins):
        self.allCoins = tuple(allCoins)

        for bag in self.allCoins:
            if bag.__class__ is not self.__class__:
                raise WizCoinException('all arguments to CoinsCollection must be Coins objects')

        self._origAmounts = tuple([copy.copy(coins) for coins in self.allCoins])


    # TODO NOTE THAT THESE PROPERTIES HAVE NO BACKING ATTRIBUTE, THEY ARE CALCULATED
    @property
    def galleons(self): # Called when `ob.galleons` property is accessed.
        """The number of galleons in all Coins."""
        return sum([coins.galleons for coins in self.allCoins])


    @property
    def sickles(self):
        """The number of sickles in all Coins."""
        return sum([coins.sickles for coins in self.allCoins])


    @property
    def knuts(self):
        """The number of knuts in all Coins."""
        return sum([coins.knuts for coins in self.allCoins])


    @property
    def value(self):
        """The value (in knuts) of all the coins in this Coins."""
        return (self.galleons * KNUTS_PER_GALLEON) + (self.sickles * KNUTS_PER_SICKLE) + (self.knuts)


    def __reversed__(self):
        return CoinsCollection(reversed(self.allCoins))


    def __enter__(self):
        self.expectedTotal = sum([coins.value for coins in self.allCoins])
        return tuple(self.allCoins)


    def __exit__(self, excType, excValue, excTraceback):
        total = sum([coins.value for coins in self.allCoins])
        if total == self.expectedTotal and excType is None:
            return # Total value has not changed.

        # TODO - eh, is this a good idea? If the coins have shifted around, fine, but if they've been added/removed then reset all the coins? I'm not convinced.
        # Maybe we should raise an exception instead.

        # Reset bags to their original amounts.
        for i, coins in enumerate(self.allCoins):
            coins.__galleons = self._origAmounts[i].__galleons
            coins.__sickles = self._origAmounts[i].__sickles
            coins.__knuts = self._origAmounts[i].__knuts

        if total != self.expectedTotal:
            raise WizCoinException('expected total value (%s) does not match current total value (%s)' % (self.expectedTotal, total))

    # TODO - overload the + and * operators?
