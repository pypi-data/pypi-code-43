import hashlib
import urllib.request

from django.core.exceptions import ValidationError


class HaveIBeenPwnedValidator:
    def validate(self, password, user=None):
        sha1 = hashlib.sha1()
        sha1.update(password.encode())
        digest = sha1.hexdigest().upper()
        prefix = digest[:5]
        url = f"https://api.pwnedpasswords.com/range/{prefix}"
        request = urllib.request.Request(url, headers={"User-Agent": "django-pwny"})
        response = urllib.request.urlopen(request)  # nosec
        for suffix_count in response.read().decode("utf-8").splitlines():
            suffix, count = suffix_count.split(":")
            if digest == f"{prefix}{suffix}":
                raise ValidationError(
                    f"Your password has been pwned {int(count):,} times!"
                )

    def get_help_text(self):
        return "Your password should not appear in a list of compromised " "passwords."
