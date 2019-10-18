import bleach
import unicodedata

SANE_TAGS = bleach.sanitizer.ALLOWED_TAGS + ["br"]


def html_sanitize(value):
    """
    Sanitize HTML in value to avoid malicious usage.
    Bleach is a bit excessive with the ampersands, and we prefer to keep it as they were.
    """
    return bleach.clean(value, tags=SANE_TAGS).replace("&amp;", "&") if value else value


def unicode_normalize(value):
    """Normalize input to ensure clean encoding in db"""
    return unicodedata.normalize("NFKC", value) if value else value
