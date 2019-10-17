from collections import OrderedDict

from rest_framework.pagination import PageNumberPagination


class RedminPagination(PageNumberPagination):
    page_query_param = 'page'
    page_size_query_param = "pageSize"
    max_page_size = 50

    def get_paginated_response(self, data):
        from rest_framework.response import Response
        result = OrderedDict([
            ('pagination', {
                "total": self.page.paginator.count,
                "pageSize": self.page.paginator.per_page,
                "current": self.page.number
            }),
            ('list', data)
        ])
        return Response(result)

    def get_next_link(self):

        from rest_framework.utils.urls import replace_query_param
        if not self.page.has_next():
            return None
        url = self.request.build_absolute_uri()
        page_number = self.page.next_page_number()
        result = replace_query_param(url, self.page_query_param, page_number)
        result = replace_query_param(result, self.page_size_query_param, self.page.paginator.per_page)
        return result

    def get_previous_link(self):
        from rest_framework.utils.urls import replace_query_param, remove_query_param
        if not self.page.has_previous():
            return None
        url = self.request.build_absolute_uri()
        page_number = self.page.previous_page_number()

        if page_number == 1:
            result = remove_query_param(url, self.page_query_param)
        else:
            result = replace_query_param(url, self.page_query_param, page_number)

        result = replace_query_param(result, self.page_size_query_param, self.page.paginator.per_page)
        return result
