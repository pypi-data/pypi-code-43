import avro.schema
import json
from avro.io import DatumReader, BinaryDecoder, AvroTypeException
from fastavro import schemaless_writer, validate
from io import BytesIO


class AvroCodec(object):
    def __init__(self, schema):
        self._raw_schema = schema
        self._avro_schema = avro.schema.parse(json.dumps(schema))
        self._reader = DatumReader(self._avro_schema)

    def dump(self, obj, fp):
        """
        Serializes obj as an avro-format byte stream to the provided
        fp file-like object stream.
        """
        if not validate(obj, self._raw_schema, raise_errors = False):
            raise AvroTypeException(self._avro_schema, obj)
        schemaless_writer(fp, self._raw_schema, obj)

    def dumps(self, obj):
        """
        Serializes obj to an avro-format byte array and returns it.
        """
        out = BytesIO()
        try:
            self.dump(obj, out)
            return out.getvalue()
        finally:
            out.close()

    def load(self, fp):
        """
        Deserializes the byte stream contents of the given file-like
        object into an object and returns it.
        """
        return self._reader.read(BinaryDecoder(fp))

    def loads(self, data):
        """
        Deserializes the given byte array into an object and returns it.
        """
        st = BytesIO(data)
        try:
            return self.load(st)
        finally:
            st.close()
