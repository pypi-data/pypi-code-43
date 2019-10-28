from django.db import models
from django.conf import settings as django_settings
from django.contrib.sites.models import Site
from django.db.models.signals import post_delete
from ulid import new as new_ulid

import json
import jsonfield

from model_utils.models import TimeStampedModel

from dj_pony.tenant.mixins import SingleTenantModelMixin
from dj_pony.tenant.settings import get_setting
from dj_pony.tenant.validators import validate_json
from dj_pony.ulidfield.models import ULIDField


# TODO: It might be good if this was swappable, or had some swappable component...
class Tenant(TimeStampedModel):
    # Its important to have a non integer pseudo-primary key for interoperability reasons.
    ulid = ULIDField(unique=True, db_index=True, default=new_ulid)
    # --------------------------------------------------------------------------------
    name = models.CharField(max_length=255)
    # TODO: The slug field should REALLY have some kind of randomization, or other autogeneration.
    #  Blank by default is a pain.
    # TODO: IDEA: Use a HashID field as slug?
    slug = models.CharField(max_length=255, unique=True, default=new_ulid)

    extra_data = jsonfield.JSONField(
        blank=True, null=True, default=get_setting("DEFAULT_TENANT_EXTRA_DATA")
    )
    settings = jsonfield.JSONField(
        blank=True, null=True, default=get_setting("DEFAULT_TENANT_SETTINGS")
    )

    def __str__(self):
        return self.name


class TenantSite(TimeStampedModel, SingleTenantModelMixin):
    tenant = models.ForeignKey(
        "Tenant", related_name="tenant_sites", on_delete=models.CASCADE
    )
    site = models.OneToOneField(
        Site, related_name="tenant_site", on_delete=models.CASCADE
    )

    def __str__(self):
        return "%s - %s" % (self.tenant.name, self.site.domain)


def post_delete_tenant_site(sender, instance, *args, **kwargs):
    # TODO: Im not 100% sure, so I'll need to confirm this, but I'm
    #  pretty sure that due to the way post_delete works, combined
    #  with the `TenantSite -> Site` relationship being defined
    #  with `on_delete=models.CASCADE`, that this is not necessary
    if instance.site:  # pragma: no branch
        instance.site.delete()


post_delete.connect(post_delete_tenant_site, sender=TenantSite)


class TenantRelationship(TimeStampedModel, SingleTenantModelMixin):
    tenant = models.ForeignKey(
        "Tenant", related_name="relationships", on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        django_settings.AUTH_USER_MODEL,
        related_name="relationships",
        on_delete=models.CASCADE,
    )
    groups = models.ManyToManyField(
        "auth.Group", related_name="user_tenant_groups", blank=True
    )
    permissions = models.ManyToManyField(
        "auth.Permission", related_name="user_tenant_permissions", blank=True
    )

    def __str__(self):
        groups_str = ", ".join([g.name for g in self.groups.all()])
        return "%s - %s (%s)" % (str(self.user), str(self.tenant), groups_str)

    class Meta:
        unique_together = [("user", "tenant")]
