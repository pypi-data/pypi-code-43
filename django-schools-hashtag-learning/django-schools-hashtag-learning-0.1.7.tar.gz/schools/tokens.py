from django.contrib.auth.tokens import PasswordResetTokenGenerator
from django.utils import six

class TokenGenerator(PasswordResetTokenGenerator):
    def _make_hash_value(self, impact_object, timestamp):
        return (
            six.text_type(impact_object.pk) + six.text_type(timestamp)
        )

account_activation_token = TokenGenerator()
