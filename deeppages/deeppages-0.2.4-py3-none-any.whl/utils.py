from django.template import Template, Context
from django.utils.deprecation import MiddlewareMixin
from django.conf import settings
from django.db.models import Q
from django.urls import reverse, NoReverseMatch
from django.core.exceptions import ObjectDoesNotExist

from .signals import page_found, page_not_found, page_requested
from .exceptions import InvalidPathException, PageNotFoundException
from .models import Page

import re


def normalize_path(path):
    ''' Remove duplicated slashes and reverse mode with/wo slash in the end '''
    from .urls import get_deeppages_path

    new_path = re.sub(r'[\/]{2,}', '/', path)

    try:
        # check if deeppages' path isn't the root path
        deeppages_path = reverse('deeppages:{}'.format(get_deeppages_path()))
    except NoReverseMatch:
        pass
    else:
        if deeppages_path != '/':
            if new_path.startswith(deeppages_path):
                new_path = new_path.replace(deeppages_path, '')
                if not new_path.startswith('/'):
                    new_path = '/{}'.format(new_path)

    return new_path[:-1] if new_path.endswith('/') else '{}/'.format(new_path)


def render_content(content, context):
    ''' Render page content '''
    ctx = Context(context or {})
    return Template(content).render(ctx)


def render_page(page, context, callback):
    ''' Render page '''
    if callback:
        page_content = callback(page, context)
    else:
        page_content = page.content

    return render_content(page_content, context)


def render_requested_page_content(sender, request, page):
    ''' Render page requested by Middleware or PageView '''
    content = page.content
    ctx = {'request': request}

    page_found.send_robust(
        sender=sender.__class__,
        page=page,
        path=page.path,
        request=request,
        content=content,
        context=ctx)

    # So, if content and/or context was changed inside the signal receiver,
    # we'll render with the new values.
    return render_content(content, ctx)


def is_acceptable_file_type(path):
    ''' Only text-based content can be accepted, any other will be ignored. '''
    filename = path.strip('/').split('/')[-1]

    accepted_exts = ['.html', '.htm', '.css', '.js', '.svg', '.txt']
    max_ext_len = max(map(len, accepted_exts))

    try:
        has_extension = filename.index('.') >= (len(filename) - max_ext_len)
    except ValueError:
        has_extension = False

    is_accepted = not has_extension or len([a for a in accepted_exts
                                            if filename.endswith(a)]) > 0

    return is_accepted


def get_page_by_path(sender, request, logger):
    ''' Get page by path and return a rendered and processed template.

    Arguments:

        sender  -- object sender
        request -- WSGIRequest object
        logger  -- logger instance

    Also, three robust signals can be dispatched from here:
        1. page_requested (after a page request, ha!)
        2. page_not_found (for non-existent pages! O'really?)
        3. and, mainly, page_found (When a page exists AND is active! Ha!
           Could you imagine that?)

    Both signals: 'page_request' and 'page_not_found' these keyword
    arguments will be received: 'path' and 'request'.

    For 'page_found':
        - path: the path (URL) requested
        - page: a deeppages.models.Page() model's instance that was found
                by its PATH
        - request: WSGIRequest object
        - context: a context dictionary (with request inside)
        - content: the page content (you can change it as you wish)

    In case of 'page_not_found', after robust signal callback has been
    returned, Django's will follow its normal flow.

    ps.: if settings.DEBUG is True, you can handle some logs for debug
         purposes.
    '''
    path = normalize_path(request.path)

    if not is_acceptable_file_type(path):
        return

    if settings.DEBUG and logger:
        logger.debug('DeepPage Path Requested: [{}]'.format(path))

    # dispatch page requested signal
    page_requested.send_robust(
        sender=sender.__class__, path=path, request=request)

    if not path:
        # Is called from an instance subclass of TemplateView ?
        if issubclass(sender.__class__, MiddlewareMixin):
            return
        else:
            raise InvalidPathException

    try:
        # try to get page directly
        page = Page.objects.exclude(is_active=False).get(
            Q(path__iexact=path) | Q(path__iexact=request.path))

    except Page.DoesNotExist:
        if settings.DEBUG and logger:
            logger.exception('DeepPage Not Found: [{}]'.format(path))

        page_not_found.send_robust(
            sender=sender.__class__,
            path=path,
            request=request)

        if issubclass(sender.__class__, MiddlewareMixin):
            return
        else:
            raise PageNotFoundException
    else:
        return render_requested_page_content(sender, request, page)


def get_page_by_name(name, context=None, callback=None):
    ''' Get page by its name and render it.

    Arguments:

        name -- Page name

    Keyword arguments:

        context -- dictionary with additional key/values that
        will be used for page content rendering (default: None)

        callback -- callback function - will be called before render the
        page content (default: None)
    '''
    if not name:
        return

    try:
        # try to get page directly
        page = Page.objects.exclude(is_active=False).get(name__iexact=name)

    except ObjectDoesNotExist:
        return

    else:
        return render_page(page, context, callback)


def get_page_by_slug(slug, context=None, callback=None):
    ''' Get page by its slug and render it.

    Arguments:

        slug -- Page's slug

    Keyword arguments:

        context -- dictionary with additional key/values that
        will be used for page content rendering (default: None)

        callback -- callback function - will be called before render the
        page content (default: None)
    '''
    if not slug:
        return

    try:
        page = Page.objects.exclude(is_active=False).get(slug__iexact=slug)

    except ObjectDoesNotExist:
        return

    else:
        return render_page(page, context, callback)
