import platform
from django.utils.functional import SimpleLazyObject
from dj_pony.tenant.settings import get_setting
from dj_pony.tenant.models import Tenant
from dj_pony.tenant.utils import import_from_string

import contextvars


if platform.python_version_tuple()[0] == "2":
    import thread as threading
else:
    import threading


def get_tenant(request):
    if not hasattr(request, "_cached_tenant"):
        tenant_retrievers = get_setting("TENANT_RETRIEVERS")

        for tenant_retriever in tenant_retrievers:
            tenant = import_from_string(tenant_retriever)(request)
            if tenant:
                request._cached_tenant = tenant
                break

        if not getattr(request, "_cached_tenant", False):
            lazy_tenant = TenantMiddleware.get_current_tenant()
            if not lazy_tenant:
                return None

            lazy_tenant._setup()
            request._cached_tenant = lazy_tenant._wrapped

        elif get_setting("ADD_TENANT_TO_SESSION"):
            try:
                request.session["tenant_slug"] = request._cached_tenant.slug
            except AttributeError:
                pass

    return request._cached_tenant


# class TenantMiddleware(object):
#     _threadmap = {}
#
#     def __init__(self, get_response):
#         self.get_response = get_response
#         # One-time configuration and initialization.
#
#     @classmethod
#     def get_current_tenant(cls):
#         try:
#             return cls._threadmap[threading.get_ident()]
#         except KeyError:
#             return None
#
#     @classmethod
#     def set_tenant(cls, tenant_slug):
#         cls._threadmap[threading.get_ident()] = SimpleLazyObject(
#             lambda: Tenant.objects.filter(slug=tenant_slug).first())
#
#     @classmethod
#     def clear_tenant(cls):
#         del cls._threadmap[threading.get_ident()]
#
#     def process_request(self, request):
#         request.tenant = SimpleLazyObject(lambda: get_tenant(request))
#         self._threadmap[threading.get_ident()] = request.tenant
#
#         return request
#
#     def process_exception(self, request, exception):
#         try:
#             del self._threadmap[threading.get_ident()]
#         except KeyError:
#             pass
#
#     def process_response(self, request, response):
#         try:
#             del self._threadmap[threading.get_ident()]
#         except KeyError:
#             pass
#         return response
#
#     def __call__(self, request):
#         # Code to be executed for each request before
#         # the view (and later middleware) are called.
#         request = self.process_request(request)
#         response = self.get_response(request)
#         return self.process_response(request, response)


#


# TODO: I really need to develop tests that properly exercise this code.
#  Thread Local vs Context Variables is complicated.


TENANT_CONTEXT_VAR = contextvars.ContextVar("tenant_context")
TENANT_THREAD_LOCAL = threading.local()


class TenantMiddleware(object):
    _use_threading = True
    context_token = None

    def __init__(self, get_response):
        self.get_response = get_response
        # One-time configuration and initialization.

    @classmethod
    def get_current_tenant(cls):
        try:
            if not cls._use_threading:
                return TENANT_CONTEXT_VAR.get()
            else:
                return TENANT_THREAD_LOCAL.tenant
        except (LookupError, AttributeError):
            return None

    @classmethod
    def set_tenant(cls, tenant_slug):
        if not cls._use_threading:
            cls.context_token = TENANT_CONTEXT_VAR.set(
                SimpleLazyObject(
                    lambda: Tenant.objects.filter(slug=tenant_slug).first()
                )
            )
        else:
            TENANT_THREAD_LOCAL.tenant = SimpleLazyObject(
                lambda: Tenant.objects.filter(slug=tenant_slug).first()
            )

    @classmethod
    def clear_tenant(cls):
        if not cls._use_threading:
            TENANT_CONTEXT_VAR.reset(cls.context_token)
        else:
            TENANT_THREAD_LOCAL.tenant = None

    def process_request(self, request):
        request.tenant = SimpleLazyObject(lambda: get_tenant(request))
        if not self._use_threading:
            self.context_token = TENANT_CONTEXT_VAR.set(request.tenant)
        else:
            # TODO: not sure i need to do anything for the thread local mode.
            pass
        return request

    def process_exception(self, request, exception):
        if not self._use_threading:
            TENANT_CONTEXT_VAR.reset(self.context_token)
        else:
            TENANT_THREAD_LOCAL.tenant = None

    def process_response(self, request, response):
        if not self._use_threading:
            TENANT_CONTEXT_VAR.reset(self.context_token)
        else:
            TENANT_THREAD_LOCAL.tenant = None
        return response

    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        request = self.process_request(request)
        response = self.get_response(request)
        return self.process_response(request, response)
