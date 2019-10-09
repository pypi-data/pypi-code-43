
from django.db.models import Count

from rest_framework.decorators import action
from rest_framework.response import Response


class AutocompleteTextFieldMixin:

    @action(detail=False)
    def autocomplete_text_field(self, request):
        field = request.GET.get('field')
        qs = self.get_queryset().values(field).filter(**{
            f'{field}__isnull': False
        }).annotate(
            num=Count(field)
        ).order_by(field)
        return Response([
            item[field] for item in qs
        ])
