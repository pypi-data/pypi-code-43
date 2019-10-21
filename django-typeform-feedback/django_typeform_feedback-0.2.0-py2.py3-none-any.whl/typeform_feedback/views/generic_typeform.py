from django.http.response import HttpResponseRedirect
from django.views.generic.detail import DetailView

from ..models import GenericTypeformFeedback


class GetQuizView(DetailView):

    model = GenericTypeformFeedback
    slug_field = 'quiz_slug'
    slug_url_kwarg = 'quiz_slug'

    def get(self, request, *args, **kwargs):
        return HttpResponseRedirect(self.get_object().url)
