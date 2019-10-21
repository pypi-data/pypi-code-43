from django.contrib.sites.shortcuts import get_current_site
from django.contrib.sites.models import Site
from django.core.handlers.wsgi import WSGIRequest
from dj_pony.tenant.models import Tenant, TenantSite
from dj_pony.tenant.settings import get_setting
from dj_pony.tenant.exceptions import TenantNotFoundError


def retrieve_by_domain(request: WSGIRequest):
    try:
        return get_current_site(request).tenant_site.tenant
    except (TenantSite.DoesNotExist, Site.DoesNotExist):
        return None
    # TODO: I'm not sure how to reach this branch.
    #  Since a TenantSite must have a Tenant and uses cascading deletes.
    except Tenant.DoesNotExist:  # pragma: no cover
        raise TenantNotFoundError()


def retrieve_by_http_header(request: WSGIRequest):
    try:
        tenant_http_header = (
            "HTTP_" + get_setting("TENANT_HTTP_HEADER").replace("-", "_").upper()
        )
        return Tenant.objects.get(slug=request.META[tenant_http_header])
    except LookupError:
        return None
    except Tenant.DoesNotExist:
        raise TenantNotFoundError()


def retrieve_by_session(request: WSGIRequest):
    try:
        return Tenant.objects.get(slug=request.session["tenant_slug"])
    except (AttributeError, LookupError, Tenant.DoesNotExist):
        return None
    # TODO: I think this may be unreachable.
    #  Since a TenantSite must have a Tenant and uses cascading deletes.
    except Tenant.DoesNotExist:  # pragma: no cover
        raise TenantNotFoundError()
