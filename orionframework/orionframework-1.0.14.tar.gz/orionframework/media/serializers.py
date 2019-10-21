from orionframework.taggable.mixins import TaggableSerializer
from rest_framework import fields
from rest_framework.fields import empty
from rest_framework.serializers import Serializer, ModelSerializer

from orionframework.media.settings import Document, Image
from orionframework.authored.serializers import UserNameSerializer


class AbstractDocumentSerializer(ModelSerializer,
                                 TaggableSerializer):
    """
    Serializer for orion.media.models.Document or orion.media.models.Image
    """

    urls = fields.DictField(read_only=True)

    type = fields.ReadOnlyField()

    extension = fields.ReadOnlyField()

    filesize = fields.ReadOnlyField()

    filename = fields.ReadOnlyField()

    thumbnails_filesize = fields.ReadOnlyField()

    category = fields.ReadOnlyField()

    created_by = UserNameSerializer(read_only=True)

    modified_by = UserNameSerializer(read_only=True)


class DocumentSerializer(AbstractDocumentSerializer):
    class Meta:
        model = Document
        exclude = ["parent_type", "parent_id", "file"]


class ImageSerializer(AbstractDocumentSerializer):
    class Meta:
        model = Image
        exclude = ["parent_type", "parent_id", "file"]


class MediaSerializer(Serializer):
    """
    Helper serializer that emulates support for polymorphic data serialization
    for multiple different types of media model classes.
    """

    def __init__(self, instance=None, data=empty, document_serializer_class=DocumentSerializer,
                 image_serializer_class=ImageSerializer, **kwargs):

        super(MediaSerializer, self).__init__(instance=instance, data=data, **kwargs)

        self.document_serializer = document_serializer_class()
        self.image_serializer = image_serializer_class()

    def to_representation(self, item):

        if isinstance(item, Image):
            return self.image_serializer.to_representation(item)
        else:
            return self.document_serializer.to_representation(item)


class DictionaryMediaSerializer(Serializer):
    """
    Serializer that renders a list of documents as dictionary where each 
    document's name is a key in the rendered map.
    """

    many = True

    serializer_class = MediaSerializer

    def __init__(self, keys=None, other_key="other", **kwargs):

        super(DictionaryMediaSerializer, self).__init__(**kwargs)

        self.other_key = other_key
        self.keys = keys

    def to_representation(self, items):
        """
        Object instance -> Dict of primitive datatypes.
        """
        map = {}

        other = []

        if self.keys:

            map[self.other_key] = other

            for key in self.keys:
                map[key] = None

        serializer = self.serializer_class()

        for item in items:

            value = serializer.to_representation(item)

            if self.keys:

                if item.name in self.keys:

                    map[item.name] = value

                else:

                    other.append(value)
            else:

                map[item.name] = value

        return map
