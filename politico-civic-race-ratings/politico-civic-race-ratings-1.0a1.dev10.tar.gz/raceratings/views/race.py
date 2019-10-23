# Imports from Django.
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.urls import reverse


# Imports from other dependencies.
from election.models import Race


# Imports from race_ratings.
from raceratings.serializers import RaceSerializer
from raceratings.views.base import BaseView


class RacePage(BaseView):
    name = "raceratings_race-page"
    path = r"race/(?P<division>\w+)/(?P<body>\w+)(?:/(?P<code>\w+))?"

    js_dev_path = "raceratings/js/main-race-app.js"
    css_dev_path = "raceratings/css/main-race-app.css"

    model = Race
    context_object_name = "race"
    template_name = "raceratings/race.html"

    def get_queryset(self):
        return self.model.objects.filter(cycle__slug="2018")

    def get_object(self, **kwargs):
        return self.get_race(
            self.kwargs.get("division"),
            self.kwargs.get("body"),
            self.kwargs.get("code"),
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        self.division = self.kwargs.get("division")
        self.body = self.kwargs.get("body")
        self.code = self.kwargs.get("code")

        context["secret"] = getattr(settings, "RACE_RATINGS_SECRET_KEY", "")

        return {
            **context,
            **self.get_paths_context(production=context["production"]),
        }

    def get_publish_path(self):
        subpath = "{}/{}".format(self.division, self.body)
        if self.code:
            subpath = "{}/{}".format(subpath, self.code)

        return "election-results/2018/ratings/{}".format(subpath)

    def get_serialized_data(self):
        race = self.get_race(self.division, self.body, self.code)
        return RaceSerializer(race).data

    def get_race(self, division, body, code):
        kwargs = {}

        if code:
            if code == "special":
                kwargs["special"] = True
            else:
                kwargs["office__division__code"] = code
                kwargs["special"] = False
        else:
            kwargs["special"] = False

        if body == "governor":
            kwargs["office__slug"] = "{}-governor".format(division)
        else:
            kwargs["office__body__slug"] = body

        if body == "house":
            kwargs["office__division__parent__slug"] = division
        else:
            kwargs["office__division__slug"] = division

        return get_object_or_404(Race, **kwargs)

    def get_extra_static_paths(self, production):
        if production:
            return {"data": "data.json"}
        return {
            "data": reverse(
                "raceratings_api_race-detail", args=[self.object.uid]
            )
        }
