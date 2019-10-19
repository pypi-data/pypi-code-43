from django.contrib.auth.models import Group
from edc_permissions.utils import add_permissions_to_group_by_codenames

from ..codenames import ae_review
from ..group_names import AE_REVIEW


def update_ae_review_group_permissions():
    group_name = AE_REVIEW
    group = Group.objects.get(name=group_name)
    group.permissions.clear()
    add_permissions_to_group_by_codenames(group, ae_review)
    return group_name
