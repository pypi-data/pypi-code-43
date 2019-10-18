from edc_adverse_event.view_mixins import (
    NewTmgAeListboardView as BaseNew,
    OpenTmgAeListboardView as BaseOpen,
    ClosedTmgAeListboardView as BaseClosed,
)


class NewTmgAeListboardView(BaseNew):

    listboard_back_url = "ambition_dashboard:tmg_home_url"
    navbar_name = "ambition_dashboard"


class OpenTmgAeListboardView(BaseOpen):

    listboard_back_url = "ambition_dashboard:tmg_home_url"
    navbar_name = "ambition_dashboard"


class ClosedTmgAeListboardView(BaseClosed):

    listboard_back_url = "ambition_dashboard:tmg_home_url"
    navbar_name = "ambition_dashboard"
