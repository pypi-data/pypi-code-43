from django.conf import settings
from django.core.paginator import (
    Paginator,
    PageNotAnInteger,
    EmptyPage,
)


def items_at_page(items, items_per_pages, page_number):
    """Get items at given page"""
    paginator = Paginator(
        items,
        items_per_pages,
    )
    items = []
    try:
        items = paginator.page(page_number)
    except PageNotAnInteger:
        items = paginator.page(1)
    except EmptyPage:
        items = paginator.page(paginator.num_pages)
    return items
