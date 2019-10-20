# NLDSL (c) 2019 by Kevin Kiefer <abc.kiefer@gmail.com>, Heidelberg University
#
# NLDSL is licensed under a
# Creative Commons Attribution-NonCommercial 3.0 Unported License.
#
# You should have received a copy of the license along with this
# work.  If not, see <http://creativecommons.org/licenses/by-nc/3.0/>.

"""A selection of  exception classes to describe incomplete or incorrect DSL Arguments.
All of these exceptions will be catched by the CodeGenerator class and converted into
a code recommendation.
"""




class DSLError(Exception):
    """Base class for all DSL related exceptions."""




class DSLArgumentError(DSLError):
    """This exception indicates that a DSL argument is missing or incorrect.

    Args:
        message (str): A string containing a description of the error
        rule (grammar rule): An instance of grammar rule class.
    """

    def __init__(self, message, rule):
        """Please see help(DSLArgumentError)."""
        super().__init__("message: {}, rule: {}".format(message, rule))
        self.message = message
        self.rule = rule


    def __reduce__(self):
        """Allow this exceptions to be pickled.

        Returns:
            (tuple) DSLArgumentError and a tuple of the constructor arguments.
        """
        return (DSLArgumentError, (self.message, self.rule))




class DSLFunctionError(DSLError):
    """This exception indicates that a DSL function failed to generate code

    This exceptions is usually raised due to a previous DSLArgumentError exception.

    Args:
        message (str): A string containing a description of the error
        rule (grammar rule): An instance of grammar rule class.
    """

    def __init__(self, message, rule, doc=""):
        """Please see help(DSLFunctionError)."""
        super().__init__("message: {}, rule: {}".format(message, rule))
        self.message = message
        self.rule = rule
        self.doc = doc


    def __reduce__(self):
        """Allow this exceptions to be pickled.

        Returns:
            (tuple) DSLFunctionError and a tuple of the constructor arguments.
        """
        return (DSLFunctionError, (self.message, self.rule))
