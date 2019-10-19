from rest_framework import serializers
from rest_framework.serializers import HyperlinkedIdentityField, SerializerMethodField
from ..models import CategoryModel
from ..models import ArticleModel


class CategorySerializer(serializers.ModelSerializer):
    detail_url = HyperlinkedIdentityField(
        view_name = "djangopost:category_retrieve_viewset",
        lookup_field = "slug"
    )

    update_url = HyperlinkedIdentityField(
        view_name = "djangopost:category_update_viewset",
        lookup_field = "slug"
    )

    delete_url = HyperlinkedIdentityField(
        view_name = "djangopost:category_destroy_viewset",
        lookup_field = "slug"
    )

    # description = SerializerMethodField()

    class Meta:
        model = CategoryModel
        fields = ['serial', 'title', 'slug', 'description', 'author',
                  'status', 'detail_url', 'update_url', 'delete_url']

    # def get_description(self, obj):
    #     return str(obj.description[:100])


class ArticleSerializer(serializers.ModelSerializer):

    detail_url = HyperlinkedIdentityField(
        view_name = "djangopost:article_retrieve_viewset",
        lookup_field = "slug"
    )

    update_url = HyperlinkedIdentityField(
        view_name = "djangopost:article_update_viewset",
        lookup_field = "slug"
    )

    delete_url = HyperlinkedIdentityField(
        view_name = "djangopost:article_destroy_viewset",
        lookup_field = "slug"
    )

    # cover_image = SerializerMethodField()
    # description = SerializerMethodField()
    # shortlines = SerializerMethodField()
    # content = SerializerMethodField()

    class Meta:
        model = ArticleModel
        fields = ['serial', 'cover_image', 'title', 'slug', 'category',
                  'description', 'author','shortlines', 'content',
                  'detail_url', 'update_url', 'delete_url']

    # def get_cover_image(self, obj):
    #     try:
    #         return obj.cover_image.url 
    #     except Exception:
    #         return None

    # def get_description(self, obj):
    #     return str(obj.description[:100])

    # def get_shortlines(self, obj):
    #     return str(obj.shortlines[:100])

    # def get_content(self, obj):
    #     return str(obj.content[:100])