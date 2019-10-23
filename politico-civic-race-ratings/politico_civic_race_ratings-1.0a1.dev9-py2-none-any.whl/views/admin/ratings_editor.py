# Imports from Django.
from django.conf import settings
from django.views.generic import TemplateView


# Imports from race_ratings.
from raceratings.utils.auth import secure


@secure
class RatingsEditor(TemplateView):
    template_name = "raceratings/admin/ratings.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["secret"] = getattr(settings, "RACE_RATINGS_SECRET_KEY", "")
        return context
