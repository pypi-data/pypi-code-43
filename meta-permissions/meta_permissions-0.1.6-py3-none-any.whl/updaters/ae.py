from django.contrib.auth.models import Group
from edc_permissions.utils import add_permissions_to_group_by_codenames

from ..codenames import ae
from ..group_names import AE


def update_ae_group_permissions():
    group_name = AE
    group = Group.objects.get(name=group_name)
    group.permissions.clear()
    add_permissions_to_group_by_codenames(group, ae)
    return group_name
