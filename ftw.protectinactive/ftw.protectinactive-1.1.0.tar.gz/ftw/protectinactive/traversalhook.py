from AccessControl.unauthorized import Unauthorized
from datetime import datetime
from ftw.protectinactive.registry import IProtectInactiveSettings
from plone.app.dexterity.behaviors.metadata import IPublication
from plone import api
from Products.CMFCore.interfaces import IContentish
from Products.CMFCore.interfaces import ISiteRoot
from zExceptions import NotFound
from zope.component.hooks import getSite


def protect_incative_hook(event):
    """ Protect inactive content from unauthorized access. """

    site = getSite()
    if not site:
        return

    context = findContext(event.request)

    for permission in ['Modify portal content', 'Request review', 'Review portal content']:
        if api.user.has_permission(permission, obj=context):
            return

    publication_date, expiration_date = getPublicationDates(context)

    if isUnreleased(publication_date) or isExpired(expiration_date):
        # raise configured exception
        exception_type = api.portal.get_registry_record(
            name='exception_type', interface=IProtectInactiveSettings)
        exception = {
            'Unauthorized': Unauthorized,
            'NotFound': NotFound
        }.get(exception_type, NotImplementedError)

        raise exception()


def isUnreleased(publication_date):
    """ Checks if the publication date is in the future.
        If it is it checks if the user has access to unreleased content.
    """
    now = datetime.now()
    return (publication_date and
            now < publication_date and
            not api.user.has_permission('Access future portal content'))


def isExpired(expiration_date):
    """ Checks if the expiration date has been exceeded.
        If it is it check if the user has access to expired content.
    """
    now = datetime.now()
    return (expiration_date and
            now > expiration_date and
            not api.user.has_permission('Access inactive portal content'))


def getPublicationDates(context):
    """ Returns the publication and the expiration dates.
    """
    publication = IPublication(context, None)
    if not publication:  # IPublication is not supported
        return None, None

    return publication.effective, publication.expires


def findContext(request):
    """Find the context from the request
       copied from: https://github.com/plone/plone.app.theming/blob/master/src/plone/app/theming/utils.py#L171
    """
    published = request.get('PUBLISHED', None)
    context = getattr(published, '__parent__', None)
    if context is not None:
        return context

    for parent in request.PARENTS:
        if IContentish.providedBy(parent) or ISiteRoot.providedBy(parent):
            return parent

    return request.PARENTS[0]
