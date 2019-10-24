from taggit_serializer.serializers import TagListSerializerField, TaggitSerializer


class TaggableSerializer(TaggitSerializer):
    tags = TagListSerializerField()
