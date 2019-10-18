class AbstractSerializer(object):

    """Abstract base class of all serializers and deserializers."""

    def __getitem__(self, key):
        """Gets a child serializer.
        This operator creates a _child_ serializer represented by the given
        key.
        Args:
            key (str): Name of the child serializer.
        """
        raise NotImplementedError

    def __call__(self, key, value):
        """Serializes or deserializes a value by given name.
        This operator saves or loads a value by given name.
        If this is a serializer, then the value is simply saved at the key.
        Note that some type information might be missed depending on the
        implementation (and the target file format).
        If this is a deserializer, then the value is loaded by the key. The
        deserialization differently works on scalars and arrays. For scalars,
        the ``value`` argument is used just for determining the type of
        restored value to be converted, and the converted value is returned.
        For arrays, the restored elements are directly copied into the
        ``value`` argument. String values are treated like scalars.
        .. note::
           Serializers and deserializers are required to
           correctly handle the ``None`` value. When ``value`` is ``None``,
           serializers save it in format-dependent ways, and deserializers
           just return the loaded value. When the saved ``None`` value is
           loaded by a deserializer, it should quietly return the ``None``
           value without modifying the ``value`` object.
        Args:
            key (str): Name of the serialization entry.
            value (scalar, numpy.ndarray, cupy.ndarray, None, or str):
                Object to be (de)serialized.
                ``None`` is only supported by deserializers.
        Returns:
            Serialized or deserialized value.
        """
        raise NotImplementedError


class Serializer(AbstractSerializer):

    """Base class of all serializers."""

    def save(self, obj):
        """Saves an object by this serializer.
        This is equivalent to ``obj.serialize(self)``.
        Args:
            obj: Target object to be serialized.
        """
        obj.serialize(self)

class DictionarySerializer:

    """Serializer for dictionary.
    This is the standard serializer in Chainer. The hierarchy of objects are
    simply mapped to a flat dictionary with keys representing the paths to
    objects in the hierarchy.
    .. note::
       Despite of its name, this serializer DOES NOT serialize the
       object into external files. It just build a flat dictionary of arrays
       that can be fed into :func:`numpy.savez` and
       :func:`numpy.savez_compressed`. If you want to use this serializer
       directly, you have to manually send a resulting dictionary to one of
       these functions.
    Args:
        target (dict): The dictionary that this serializer saves the objects
            to. If target is None, then a new dictionary is created.
        path (str): The base path in the hierarchy that this serializer
            indicates.
    Attributes:
        ~DictionarySerializer.target (dict): The target dictionary.
            Once the serialization completes, this dictionary can be fed into
            :func:`numpy.savez` or :func:`numpy.savez_compressed` to serialize
            it in the NPZ format.
    """

    def __init__(self, target=None, path=''):
        self.target = {} if target is None else target
        self.path = path

    def __getitem__(self, key):
        key = key.strip('/')
        return DictionarySerializer(self.target, self.path + key + '/')

    def __call__(self, key, value):
        key = key.lstrip('/')
        self.target[self.path + key] = (
            _cpu._to_cpu(value) if value is not None
            else numpy.asarray(None))
        return value
