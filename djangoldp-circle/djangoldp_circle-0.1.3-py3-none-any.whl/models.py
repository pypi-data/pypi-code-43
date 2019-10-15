from django.conf import settings
from django.db import models

from djangoldp.models import Model


class Circle(Model):
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255, blank=True)
    creationDate = models.DateField(auto_now_add=True)
    team = models.ManyToManyField(settings.AUTH_USER_MODEL, through="CircleMember", blank=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="owned_circles", on_delete=models.DO_NOTHING)
    jabberID = models.CharField(max_length=255, blank=True, null=True)
    jabberRoom = models.BooleanField(default=True)

    class Meta:
        auto_author = 'owner'
        nested_fields = ["team"]
        anonymous_perms = ["view"]
        authenticated_perms = ["inherit", "add"]
        owner_perms = ["inherit", "change", "delete"]
        container_path = 'circles/'
        rdf_type = 'hd:circle'

    def __str__(self):
        return self.name


class CircleMember(Model):
    circle = models.ForeignKey(Circle, on_delete=models.CASCADE, related_name='members')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        depth = 0

    def __str__(self):
        return str(self.id)


CircleMember._meta.container_path = "circle-members/"
