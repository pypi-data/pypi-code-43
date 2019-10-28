from django.templatetags.static import static
from django.utils.translation import gettext_lazy as _

from rijkshuisstijl.templatetags.rijkshuisstijl import register
from .rijkshuisstijl_helpers import merge_config, parse_kwarg


@register.inclusion_tag('rijkshuisstijl/components/footer/footer.html', takes_context=True)
def footer(context, **kwargs):
    """
    Renders a page footer which may contain (django-sitetree) navigation. Use "footer" as the sitetree alias.

    Example:

        {% footer config=config %}
        {% footer option1='foo' option2='bar' %}

    Available options:

        - class: Optional, a string with additional CSS classes.

    :param context:
    :param kwargs:
    """
    kwargs = merge_config(kwargs)

    # kwargs
    kwargs['class'] = kwargs.get('class', None)

    kwargs['request'] = context['request']

    kwargs['config'] = kwargs
    return kwargs


@register.inclusion_tag('rijkshuisstijl/components/header/header.html')
def header(**kwargs):
    """
    Renders a page header.

    Example:

        {% header config=config %}
        {% header option1='foo' option2='bar' %}

    Available options:

        - class: Optional, a string with additional CSS classes.

    :param kwargs:
    """
    kwargs = merge_config(kwargs)

    # kwargs
    kwargs['class'] = kwargs.get('class', None)

    kwargs['config'] = kwargs
    return kwargs


@register.inclusion_tag('rijkshuisstijl/components/image/image.html')
def image(**kwargs):
    """
    Renders an image.

    Example:

        {% image config=config %}
        {% image option1='foo' option2='bar' %}

    Available options:

        - alt: Required, The alt text for the image.
        - src: Required, The url to the image (see mobile_src, tablet_src and laptop src).

        - class: Optional, a string with additional CSS classes.
        - href: Optional, an optional url to link to.
        - mobile_src: Optional, Specifies an image url specific to mobile screen sizes.
        - tablet_src: Optional, Specifies an image url specific to tablet screen sizes.
        - laptop_src: Optional, Specifies an image url specific to laptop screen sizes.
        - width: Optional, Sets the width attribute on the image.
        - height: Optional, Sets the height attribute on the image.
        - hide_on_error: Optional, if true, hides the image (visibility: hidden) when loading fails.


    :param kwargs:
    """
    kwargs = merge_config(kwargs)
    kwargs['alt'] = kwargs.get('alt', '')
    kwargs['class'] = kwargs.get('class', None)
    kwargs['href'] = kwargs.get('href', '')
    kwargs['src'] = kwargs.get('src', '')
    kwargs['mobile_src'] = kwargs.get('mobile_src', None)
    kwargs['tablet_src'] = kwargs.get('tablet_src', None)
    kwargs['laptop_src'] = kwargs.get('laptop_src', None)
    kwargs['width'] = kwargs.get('width', None)
    kwargs['height'] = kwargs.get('height', None)
    kwargs['hide_on_error'] = kwargs.get('hide_on_error', False)

    kwargs['config'] = kwargs
    return kwargs


@register.inclusion_tag('rijkshuisstijl/components/login-bar/login-bar.html', takes_context=True)
def login_bar(context, **kwargs):
    """
    Renders a login bar.

    Example:

        {% login_bar config=config %}
        {% login_bar option1='foo' option2='bar' %}

    Available options:

        - details_url: Required, The url to link to when the username is clicked.
        - logout_url: Required, The url to link to when the logout link is clicked.
        - login_url: Required, The url to link to when the login link is clicked.
        - registration_url: Required, The url to link to when the register link is clicked.

        - class: Optional, a string with additional CSS classes.
        - label_login: Optional, alternative label for the login link.
        - label_logged_in_as: Optional, alternative label for the logged in as label.
        - label_logout: Optional, alternative label for the logout link.
        - label_request_account: Optional, alternative label for the registration link.


    :param context:
    :param kwargs:
    """
    kwargs = merge_config(kwargs)

    # i18n
    kwargs['label_login'] = kwargs.get('label_login', _('Inloggen'))
    kwargs['label_logged_in_as'] = kwargs.get('label_logged_in_as', _('Ingelogd als'))
    kwargs['label_logout'] = kwargs.get('label_logout', _('Uitloggen'))
    kwargs['label_request_account'] = kwargs.get('label_request_account', _('Account aanvragen'))

    # kwargs
    kwargs['details_url'] = kwargs.get('details_url', '#')
    kwargs['logout_url'] = kwargs.get('logout_url', '#')
    kwargs['login_url'] = kwargs.get('login_url', '#')
    kwargs['registration_url'] = kwargs.get('registration_url', '#')

    kwargs['request'] = context['request']
    kwargs['config'] = kwargs
    return kwargs


@register.inclusion_tag('rijkshuisstijl/components/logo/logo.html')
def logo(**kwargs):
    """
    Renders the logo.

    Example:

        {% logo config=config %}
        {% logo option1='foo' option2='bar' %}

    Available options:

        - alt: Required, The alt text for the image.
        - src: Required, The url to the image (see mobile_src).
        - mobile_src: Required, Specifies an image url specific to mobile screen sizes.

        - class: Optional, a string with additional CSS classes.


    :param kwargs:
    """
    kwargs = merge_config(kwargs)

    # kwargs
    kwargs['alt'] = kwargs.get('alt', _('Logo Rijksoverheid'))
    kwargs['src'] = kwargs.get('src', static('rijkshuisstijl/components/logo/logo-tablet.svg'))
    kwargs['mobile_src'] = kwargs.get('mobile_src', static('rijkshuisstijl/components/logo/logo-mobile.svg'))

    kwargs['config'] = kwargs
    return kwargs


@register.inclusion_tag('rijkshuisstijl/components/navigation-bar/navigation-bar.html', takes_context=True)
def navigation_bar(context, **kwargs):
    """
    Renders a navigation bar which may contain (django-sitetree) navigation. Use "navigation-bar" as the sitetree alias.

    Example:

        {% navigation_bar config=config %}
        {% navigation_bar option1='foo' option2='bar' %}

    Available options:

        - details_url: Required, The url to link to when the username is clicked.
        - logout_url: Required, The url to link to when the logout link is clicked.
        - login_url: Required, The url to link to when the login link is clicked.
        - registration_url: Required, The url to link to when the register link is clicked.

        - class: Optional, a string with additional CSS classes.
        - label_login: Optional, alternative label for the login link.
        - label_logged_in_as: Optional, alternative label for the logged in as label.
        - label_logout: Optional, alternative label for the logout link.
        - label_request_account: Optional, alternative label for the registration link.
        - search_url: Optional, The url to send the search query to, setting no url (default) disables search.
        - search_placeholder: Optional, alternative label to show as search input placeholder.
        - search_method: Optional, The method to use for the search form.
        - search_name: Optional, The method to use for the search input.


    :param context:
    :param kwargs:
    """
    kwargs = merge_config(kwargs)

    # i18n
    kwargs['label_login'] = kwargs.get('label_login', _('Inloggen'))
    kwargs['label_logged_in_as'] = kwargs.get('label_logged_in_as', _('Ingelogd als'))
    kwargs['label_logout'] = kwargs.get('label_logout', _('Uitloggen'))
    kwargs['label_request_account'] = kwargs.get('label_request_account', _('Account aanvragen'))

    # kwargs
    kwargs['details_url'] = kwargs.get('details_url', '#')
    kwargs['logout_url'] = kwargs.get('logout_url', '#')
    kwargs['login_url'] = kwargs.get('login_url', '#')
    kwargs['registration_url'] = kwargs.get('registration_url', '#')
    kwargs['search_url'] = kwargs.get('search_url', None)
    kwargs['search_placeholder'] = kwargs.get('search_placeholder', None)
    kwargs['search_method'] = kwargs.get('search_method', 'get')
    kwargs['search_name'] = kwargs.get('search_name', 'q')

    kwargs['request'] = context['request']
    kwargs['config'] = kwargs
    return kwargs


@register.inclusion_tag('rijkshuisstijl/components/search/search.html', takes_context=True)
def search(context, **kwargs):
    """
    Renders a search form.

    Example:

        {% search config=config %}
        {% search option1='foo' option2='bar' %}

    Available options:

        - action: Required, The url to send the search query to.

        - class: Optional, a string with additional CSS classes.
        - label_placeholder: Optional, alternative label to show as placeholder.
        - name: Optional, The method to use for the search input, defaults to 'query'.
        - method: Optional, The method to use for the search form, defaults to 'GET'.


    :param context:
    :param kwargs:
    """
    kwargs = merge_config(kwargs)
    request = context['request']

    # kwargs
    kwargs['action'] = kwargs.get('action', '')
    kwargs['class'] = kwargs.get('class', None)
    kwargs['method'] = kwargs.get('method', 'GET')
    kwargs['name'] = kwargs.get('name', 'query')
    kwargs['label_placeholder'] = kwargs.get('label_placeholder', _('Zoeken'))

    request_dict = getattr(request, kwargs['method'], {})
    kwargs['value'] = request_dict.get(kwargs['name'], '')

    kwargs['request'] = context['request']
    kwargs['config'] = kwargs
    return kwargs


@register.inclusion_tag('rijkshuisstijl/components/skiplink/skiplink.html')
def skiplink(**kwargs):
    """
    Renders a skiplink (jump to content) for screen readers.
    Should be used with skiplink_target.

    Example:

        {% skiplink config=config %}
        {% skiplink option1='foo' option2='bar' %}

    Available options:

        - class: Optional, a string with additional CSS classes.
        - label_placeholder: Optional, alternative label to show as label.
        - target: Optional, The id of of the skiplink_target, defaults to 'skiplink-target'.


    :param kwargs:
    """
    kwargs = merge_config(kwargs)

    # i18n
    kwargs['label_to_content'] = parse_kwarg(kwargs, 'label_to_content', _('Direct naar de inhoud.'))

    # kwargs
    kwargs['target'] = '#' + kwargs.get('target', 'skiplink-target')

    kwargs['config'] = kwargs
    return kwargs


@register.inclusion_tag('rijkshuisstijl/components/skiplink/skiplink-target.html')
def skiplink_target(**kwargs):
    """
    Renders a skiplink (jump to content) target for screen readers.
    Should be used with skiplink.

    Example:

        {% skiplink_target config=config %}
        {% skiplink_target option1='foo' option2='bar' %}

    Available options:

        - class: Optional, a string with additional CSS classes.
        - id: Optional, The id of of the skiplink_target, defaults to 'skiplink-target'.


    :param kwargs:
    """
    kwargs = merge_config(kwargs)

    # kwargs
    kwargs['id'] = kwargs.get('id', 'skiplink-target')

    kwargs['config'] = kwargs
    return kwargs


@register.inclusion_tag('rijkshuisstijl/components/textbox/textbox.html')
def textbox(**kwargs):
    """
    Renders a textbox.

    Example:

        {% textbox config=config %}
        {% textbox option1='foo' option2='bar' %}

    Available options:

        - class: Optional, a string with additional CSS classes.
        - status: Optional, A status string from the Django messages framework, styling the textbox accordingly.
        - title: Optional, Title to show.
        - text: Optional, Text to show.
        - wysiwyg: Optional, Raw HTML to be shown, styled automatically.


    :param kwargs:
    """
    kwargs = merge_config(kwargs)

    # kwargs
    kwargs['class'] = kwargs.get('class', None)
    kwargs['status'] = kwargs.get('status', None)
    kwargs['title'] = kwargs.get('title', None)
    kwargs['text'] = kwargs.get('text', None)
    kwargs['wysiwyg'] = kwargs.get('wysiwyg')
    kwargs['urlize'] = kwargs.get('urlize', True)

    kwargs['config'] = kwargs
    return kwargs
