__all__ = [
    'NotSetType', 
    'NotSet', 
    'EnumStringification', 
    ]

class NotSetType( type ):
  def __bool__(self):
    return False
  __nonzero__ = __bool__
  def __repr__(self):
    return "<+NotSet+>"
  def __str__(self):
    return "<+NotSet+>"

class NotSet( object ):
  """As None, but can be used with retrieve_kw to have a unique default value
  though all job hierarchy."""
  __metaclass__ = NotSetType

class EnumStringification( object ):
  "Adds 'enum' static methods for conversion to/from string"

  _ignoreCase = False

  @classmethod
  def tostring(cls, val):
    "Transforms val into string."
    from Akuanduba.core.utilities  import get_attributes
    for k, v in get_attributes(cls, getProtected = False):
      if v==val:
        return k
    return None

  @classmethod
  def fromstring(cls, str_):
    "Transforms string into enumeration."
    from Akuanduba.core.utilities  import get_attributes
    if not cls._ignoreCase:
      return getattr(cls, str_, None)
    else:
      allowedValues = [attr for attr in get_attributes(cls) if not attr[0].startswith('_')]
      try:
        idx = [attr[0].upper() for attr in allowedValues].index(str_.upper().replace('-','_'))
      except ValueError:
        raise ValueError("%s is not in enumeration. Use one of the followings: %r" % (str_, allowedValues) )
      return allowedValues[idx][1]

  @classmethod
  def retrieve(cls, val):
    """
    Retrieve int value and check if it is a valid enumeration string or int on
    this enumeration class.
    """
    from Akuanduba.core.utilities import get_attributes
    allowedValues = [attr for attr in get_attributes(cls) if not attr[0].startswith('_')]
    try:
      # Convert integer string values to integer, if possible:
      val = int(val)
    except ValueError:
      pass
    if type(val) is str:
      oldVal = val
      val = cls.fromstring(val)
      if val is None:
          raise ValueError("String (%s) does not match any of the allowed values %r." % \
              (oldVal, allowedValues))
    else:
      if not val in [attr[1] for attr in allowedValues]:
        raise ValueError(("Attempted to retrieve val benchmark "
            "with a enumeration value which is not allowed. Use one of the followings: "
            "%r") % allowedValues)
    return val

  @classmethod
  def sretrieve(cls, val):
    "Return enumeration equivalent value in string if it is a valid enumeration code."
    return cls.tostring(cls.retrieve(val))

  @classmethod
  def optionList(cls):
    from operator import itemgetter
    from Akuanduba.core.utilities import get_attributes
    return [v for v in sorted(get_attributes( cls, getProtected = False), key=itemgetter(1))]

  @classmethod
  def stringList(cls):
    from operator import itemgetter
    from Akuanduba.core.utilities import get_attributes
    return [v[0] for v in sorted(get_attributes( cls, getProtected = False), key=itemgetter(1))]

  @classmethod
  def intList(cls):
    from operator import itemgetter
    from Akuanduba.core.utilities import get_attributes
    return [v[1] for v in sorted(get_attributes( cls, getProtected = False), key=itemgetter(1))]