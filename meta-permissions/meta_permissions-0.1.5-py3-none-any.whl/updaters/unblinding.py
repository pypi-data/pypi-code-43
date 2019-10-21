from django.contrib.auth.models import Group
from edc_permissions.utils import add_permissions_to_group_by_codenames

from ..codenames import unblinding_reviewers, unblinding_requestors
from ..group_names import UNBLINDING_REVIEWERS, UNBLINDING_REQUESTORS


def update_unblinding_requestors_group_permissions():
    group_name = UNBLINDING_REQUESTORS
    group = Group.objects.get(name=group_name)
    group.permissions.clear()
    add_permissions_to_group_by_codenames(group, unblinding_requestors)
    return group_name


def update_unblinding_reviewers_group_permissions():
    group_name = UNBLINDING_REVIEWERS
    group = Group.objects.get(name=group_name)
    group.permissions.clear()
    add_permissions_to_group_by_codenames(group, unblinding_reviewers)
    return group_name
