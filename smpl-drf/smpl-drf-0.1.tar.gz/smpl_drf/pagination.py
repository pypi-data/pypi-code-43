
from django.utils import timezone

from rest_framework.response import Response
from rest_framework import pagination


class Pagination(pagination.PageNumberPagination):

    page_size = 100
    max_page_size = 100
    page_size_query_param = 'page_size'

    def get_paginated_response(self, data, **kwargs):
        return Response(dict(
            total=self.page.paginator.count,
            timestamp=timezone.now().timestamp(),
            pagination=dict(
                next=self.page.next_page_number() if self.page.has_next() else None,
                previous=self.page.previous_page_number() if self.page.has_previous() else None,
                next_link=self.get_next_link(),
                previous_link=self.get_previous_link(),
                per_page=self.page.paginator.per_page,
                page=self.page.number,
                total_pages=self.page.paginator.num_pages
            ),
            results=data,
            **kwargs
        ))


def get_pagination_class(**kwargs):
    return type('AutoPagination', (Pagination,), kwargs)
