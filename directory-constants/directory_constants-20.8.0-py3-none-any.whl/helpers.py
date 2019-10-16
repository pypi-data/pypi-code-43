from django.conf import settings


# UrlString is just a convenience wrapper around a string for making it easy to build url strings.
# It borrows the `/` syntax from `pathlib` to allow for the building of natural looking urls.
#
# eg home = UrlString('https://example.com')
# new_url = home / 'foo' / 'bar'
#
# which returns 'https://example.com/foo/bar/'
class UrlString(str):
    def __truediv__(self, other):
        base = self.strip('/')
        path = other.strip('/')
        return UrlString(f'{base}/{path}/')


def get_url(url_name, default):
    return UrlString(getattr(settings, url_name, None) or default)
