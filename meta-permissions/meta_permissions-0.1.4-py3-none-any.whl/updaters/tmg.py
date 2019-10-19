from django.contrib.auth.models import Group
from edc_permissions.utils import add_permissions_to_group_by_codenames

from edc_permissions.utils import (
    add_edc_action_permissions,
    add_permissions_to_group_by_app_label,
    # add_permissions_to_group_by_codenames,
    add_permissions_to_group_by_model,
    make_view_only_app_label,
    make_view_only_model,
    remove_historical_group_permissions,
    remove_permissions_by_model,
    remove_pii_permissions_from_group,
)

from ..codenames import tmg
from ..group_names import TMG
from .pii_models import pii_models


# def update_tmg_group_permissions():
#     group_name = TMG
#     group = Group.objects.get(name=group_name)
#     group.permissions.clear()
#     add_permissions_to_group_by_codenames(group, tmg)
#     return group_name


def update_tmg_group_permissions():
    group_name = TMG
    group = Group.objects.get(name=group_name)
    group.permissions.clear()

    # edc_action_item
    add_edc_action_permissions(group, allow_delete=True)
    make_view_only_model(group, "edc_action_item.actiontype")
    make_view_only_model(group, "edc_action_item.reference")

    # meta_ae
    add_permissions_to_group_by_app_label(group, "meta_ae")
    make_view_only_app_label(group, "meta_ae")
    add_permissions_to_group_by_model(group, "meta_ae.aetmg")
    add_permissions_to_group_by_model(group, "meta_ae.historicalaetmg")
    add_permissions_to_group_by_model(group, "meta_ae.deathreporttmg")
    add_permissions_to_group_by_model(group, "meta_ae.historicaldeathreporttmg")
    add_permissions_to_group_by_model(group, "meta_ae.deathreporttmgsecond")
    add_permissions_to_group_by_model(group, "meta_ae.historicaldeathreporttmgsecond")

    # meta_subject
    add_permissions_to_group_by_app_label(group, "meta_subject")
    make_view_only_app_label(group, "meta_subject")

    # meta_lists
    add_permissions_to_group_by_app_label(group, "meta_lists")
    make_view_only_app_label(group, "meta_lists")

    add_permissions_to_group_by_codenames(
        group,
        codenames=[
            "edc_appointment.view_historicalappointment",
            "edc_appointment.view_appointment",
        ],
    )

    # nav and dashboard
    add_permissions_to_group_by_codenames(
        group,
        codenames=[
            "edc_navbar.nav_ae_section",
            "edc_dashboard.view_ae_listboard",
            "edc_navbar.nav_tmg_section",
            "edc_navbar.nav_subject_section",
            "edc_navbar.nav_screening_section",
            "edc_dashboard.view_subject_review_listboard",
            "edc_dashboard.view_screening_listboard",
            "edc_dashboard.view_subject_listboard",
            "edc_dashboard.view_tmg_listboard",
        ],
    )

    remove_pii_permissions_from_group(group, extra_pii_models=pii_models)
    remove_historical_group_permissions(group)
    return group_name
