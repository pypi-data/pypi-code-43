from rest_framework import pagination


class DefaultResultsetPagination(pagination.PageNumberPagination):
    """
    Pagination configuration in leau of global pagination
    """
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100

class LargeResultsetPagination(pagination.PageNumberPagination):
    """
    Pagination configuration in leau of global pagination
    """
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 1000

class HugeResultsetPagination(pagination.PageNumberPagination):
    """
    Pagination configuration in leau of global pagination
    """
    page_size = 1000
    page_size_query_param = 'page_size'
    max_page_size = 1000