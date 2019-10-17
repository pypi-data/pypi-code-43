from django.contrib.admin.views.autocomplete import AutocompleteJsonView
from django.http import JsonResponse


class ModelAdminAutocompleteJsonView(AutocompleteJsonView):
    autocomplete_model = None
    lookup_field = "id"

    def get(self, request, *args, **kwargs):
        """
        Return a JsonResponse with search results of the form:
        {
            results: [{id: "123" text: "foo"}],
            pagination: {more: true}
        }
        """

        if not self.has_perm(request):
            return JsonResponse({'error': '403 Forbidden'}, status=403)

        self.term = request.GET.get('term', '')
        self.paginator_class = self.model_admin.paginator
        self.object_list = self.get_queryset()
        context = self.get_context_data()
        return JsonResponse({
            'results': [
                {'id': str(obj.pk), 'text': f"{str(obj)}"}
                for obj in context['object_list']
            ],
            'pagination': {'more': context['page_obj'].has_next()},
        })

    def get_queryset(self):
        return self.autocomplete_model.objects.filter(**{f"{self.lookup_field}__icontains": self.term})
