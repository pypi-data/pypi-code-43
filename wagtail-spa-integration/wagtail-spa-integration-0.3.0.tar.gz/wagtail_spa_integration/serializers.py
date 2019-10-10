from wagtail.contrib.redirects.models import Redirect
from rest_framework import serializers


class RedirectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Redirect
        fields = ('old_path', 'is_permanent', 'site', 'link')
