import hashlib
from django.utils.timezone import datetime


def exclude_page_type(queryset, page_models):
    qs = queryset.none()
    for model in page_models:
        qs |= queryset.not_type(model)
    return qs

def hash_draft_code(code: str, page_id: int):
    """ sha256 of date + code + page id """
    date_code = datetime.today().strftime("%Y%m%d")
    combined_code = date_code + code + str(page_id)
    hashed_code = hashlib.sha256(combined_code.encode())
    return hashed_code.hexdigest()
