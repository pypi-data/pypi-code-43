import random
import string
from django.conf import settings
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from djangoldp.models import Model


class Circle(Model):
    name = models.CharField(max_length=255)
    description = models.CharField(max_length=255, blank=True)
    creationDate = models.DateField(auto_now_add=True)
    team = models.ManyToManyField(settings.AUTH_USER_MODEL, through="CircleMember", blank=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="owned_circles", on_delete=models.DO_NOTHING)
    jabberID = models.CharField(max_length=255, blank=True, null=True, unique=True)
    jabberRoom = models.BooleanField(default=True)

    class Meta:
        auto_author = 'owner'
        owner_field = 'owner'
        nested_fields = ["team", 'members']
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

    def __str__(self):
        return str(self.circle.name) + " - " + str(self.user.name())

    class Meta:
        # TODO: As a auth I can still add someone else.
        container_path = "circle-members/"
        authenticated_perms = ["view", "add"]
        owner_perms = ["view", "add", "delete"]
        owner_field = "user"


@receiver(pre_save, sender=Circle)
def set_jabberid(sender, instance, **kwargs):
    if settings.JABBER_DEFAULT_HOST and not instance.jabberID:
        instance.jabberID = '{}@{}'.format(
            ''.join(
                [random.choice(string.ascii_letters + string.digits) for n in range(12)]
            ).lower(),
            settings.JABBER_DEFAULT_HOST
        )
        instance.jabberRoom = True
