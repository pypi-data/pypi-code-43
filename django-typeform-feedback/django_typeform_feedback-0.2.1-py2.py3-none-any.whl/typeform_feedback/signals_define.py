from django.dispatch import Signal


new_user_typeform_response = Signal(providing_args=['uuid', 'response'])
user_response_approved = Signal(providing_args=['uuid'])
