from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt


from allauth.socialaccount import providers
from allauth.socialaccount.helpers import (
    complete_social_login,
    render_authentication_error,
)
from allauth.socialaccount.models import SocialLogin

from allauth.socialaccount.providers.base import AuthError
from .forms import LoginForm
from .provider import ID4meProvider
from .utils import JSONSafeSession

from id4me_rp_client import ID4meContext, ID4meException

def login(request):
    if 'id4me' in request.GET or request.method == 'POST':
        form = LoginForm(
            dict(list(request.GET.items()) + list(request.POST.items()))
        )
        if form.is_valid():
            provider = ID4meProvider(request)
            try:
                id4me = form.cleaned_data['id4me']
                ctx = provider.get_rp_context(id4me)
                safesession = JSONSafeSession(request.session)
                SocialLogin.stash_state(request)
                url = provider.get_consent_url(ctx)
                safesession['id4me_ctx'] = ctx.to_json()
                # Fix for issues 1523 and 2072 (github django-allauth)
                # if 'next' in form.cleaned_data and form.cleaned_data['next']:
                #   auth_request.return_to_args['next'] = \
                #        form.cleaned_data['next']
                resp = HttpResponseRedirect(url)
                if (form.cleaned_data['rememberme']):
                    resp.set_cookie('id4me.user', id4me)
                return resp
            # UnicodeDecodeError:
            # see https://github.com/necaris/python3-openid/issues/1
            except (ID4meException) as e:
                if request.method == 'POST':
                    form._errors["id4me"] = form.error_class([e])
                else:
                    return render_authentication_error(
                        request,
                        ID4meProvider.id,
                        exception=e)
    else:
        form = LoginForm(initial={'next': request.GET.get('next'),
                                  'process': request.GET.get('process')})
    d = dict(form=form)
    return render(request, "id4me/login.html", d)


@csrf_exempt
def callback(request):
    provider = ID4meProvider(request)
    safesession = JSONSafeSession(request.session)
    ctx = ID4meContext.from_json(safesession['id4me_ctx'])
    try:
        if 'code' not in request.GET:
            return render_authentication_error(
                request,
                ID4meProvider.id,
                error=AuthError.DENIED if 'error' in request.GET and request.GET['error'] == 'access_denied' else AuthError.UNKNOWN,
                exception=Exception(request.GET['error_description']) if 'error_description' in request.GET else None )

        response = provider.get_response(ctx, request.GET['code'])
        login = providers.registry \
            .by_id(ID4meProvider.id, request) \
            .sociallogin_from_response(request, response)
        login.state = SocialLogin.unstash_state(request)
        ret = complete_social_login(request, login)
    except ID4meException as e:
        error = AuthError.UNKNOWN
        ret = render_authentication_error(
            request,
            ID4meProvider.id,
            error=error,
            exception=e)
    return ret
