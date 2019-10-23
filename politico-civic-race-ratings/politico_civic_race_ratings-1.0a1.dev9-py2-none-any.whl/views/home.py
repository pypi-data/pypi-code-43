# Imports from Django.
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.urls import reverse


# Imports from other dependencies.
from election.models import ElectionDay


# Imports from race_ratings.
from raceratings.views.base import BaseView


class Home(BaseView):
    name = "raceratings_home-page"
    path = ""

    js_dev_path = "raceratings/js/main-home-app.js"
    css_dev_path = "raceratings/css/main-home-app.css"

    model = ElectionDay
    context_object_name = "election_day"
    template_name = "raceratings/home.html"

    def get_queryset(self):
        return self.model.objects.all()

    def get_object(self, **kwargs):
        return get_object_or_404(ElectionDay, slug="2018-11-06")

    def get_publish_path(self):
        return (
            "election-results/2018/house-senate-race-ratings-and-predictions"
        )

    def get_serialized_data(self):
        pass

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["secret"] = getattr(settings, "RACE_RATINGS_SECRET_KEY", "")
        return {
            **context,
            **self.get_paths_context(production=context["production"]),
        }

    def get_extra_static_paths(self, production):
        if production:
            return {
                "data": "../race-ratings/data/ratings.json",
                "filters": "../race-ratings/data/filters.json",
                "body_ratings": "../race-ratings/data/body-ratings.json",
                "feed": "../race-ratings/data/feed.json",
                "historicalHouse": "../race-ratings/data/historical/house.json",
                "historicalSenate": "../race-ratings/data/historical/senate.json",
            }
        return {
            # "data": reverse("raceratings_api_ratings-api"),
            # "filters": reverse("raceratings_api_filters-api"),
            "data": "http://s3.amazonaws.com/interactives.politico.com/election-results/2018/race-ratings/data/ratings.json",
            "filters": "http://s3.amazonaws.com/interactives.politico.com/election-results/2018/race-ratings/data/filters.json",
            "body_ratings": "http://s3.amazonaws.com/interactives.politico.com/election-results/2018/race-ratings/data/body-ratings.json",
            "feed": "http://s3.amazonaws.com/interactives.politico.com/election-results/2018/race-ratings/data/feed.json",
            "historicalHouse": "http://s3.amazonaws.com/interactives.politico.com/election-results/2018/race-ratings/data/historical/house.json",
            "historicalSenate": "http://s3.amazonaws.com/interactives.politico.com/election-results/2018/race-ratings/data/historical/senate.json",
        }
