from django.contrib.auth.models import Group
from edc_permissions.utils import add_permissions_to_group_by_codenames

from ..codenames import rando
from ..group_names import RANDO


def update_rando_group_permissions():
    group_name = RANDO
    group = Group.objects.get(name=group_name)
    group.permissions.clear()
    add_permissions_to_group_by_codenames(group, rando)
    return group_name
