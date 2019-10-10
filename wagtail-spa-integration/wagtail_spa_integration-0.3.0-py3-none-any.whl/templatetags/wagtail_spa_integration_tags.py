from django.conf import settings
from django import template
from ..utils import hash_draft_code

register = template.Library()

@register.simple_tag(takes_context=True)
def get_preview_code(context):
    page_id = context.request.resolver_match.args[0]
    return hash_draft_code(settings.PREVIEW_DRAFT_CODE, int(page_id))
