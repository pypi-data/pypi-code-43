from django.core.files import File
from django.http import HttpResponse, HttpResponseForbidden
import magic

from .. import settings


def get_media_response(request, data, permissions=None, headers=None):
    # For compatibility purpose
    content, url = None, None
    if isinstance(data, (File, )):
        content, url = data, data.url
    else:
        # https://docs.djangoproject.com/fr/2.1/ref/request-response/#passing-iterators # noqa
        content, url = open(data['path'], mode='rb'), data['url']

    filetype = magic.from_buffer(content.read(1024), mime=True)
    content.seek(0)

    if isinstance(permissions, list):
        if not set(permissions).intersection(
                request.user.get_all_permissions()):
            return HttpResponseForbidden()

    response = HttpResponse(content_type='application/octet-stream')
    if isinstance(headers, dict):
        for header, value in headers.items():
            response[header] = value

    if settings.MEDIA_ACCEL_REDIRECT:
        response['X-Accel-Redirect'] = f'{url}'
    else:
        response.content = content.read()
        response.content_type = filetype

    return response
