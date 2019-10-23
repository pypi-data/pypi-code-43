from dj_pony.tenant.helpers import get_current_tenant


# TODO: Do I really need this?
def current_tenant(request):
    return {"tenant": get_current_tenant()}
