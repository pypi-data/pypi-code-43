from django.contrib.auth.models import Group
from edc_permissions.utils import add_permissions_to_group_by_codenames

from ..codenames import screening
from ..group_names import SCREENING


def update_screening_group_permissions():
    group_name = SCREENING
    group = Group.objects.get(name=group_name)
    group.permissions.clear()
    add_permissions_to_group_by_codenames(group, screening)
    return group_name
