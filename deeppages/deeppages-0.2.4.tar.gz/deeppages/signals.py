from django.dispatch import Signal


page_requested = Signal(providing_args=['path', 'request'])
page_not_found = Signal(providing_args=['path', 'request'])
page_found = Signal(providing_args=[
    'path', 'request', 'page', 'content', 'context'])
