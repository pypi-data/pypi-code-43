from edc_adverse_event.views import DeathListboardView as Base


class DeathListboardView(Base):

    navbar_name = "ambition_dashboard"
    listboard_back_url = "ambition_dashboard:tmg_home_url"
