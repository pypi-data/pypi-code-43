from django.urls import reverse
from django.utils.http import urlencode

from allauth.socialaccount.providers.base import Provider, ProviderAccount
from allauth.socialaccount.app_settings import QUERY_EMAIL, EMAIL_REQUIRED, EMAIL_VERIFICATION

from id4me_rp_client import ID4meClient, ID4meClaimsRequest, ID4meClaimRequestProperties, OIDCClaim
from uuid import uuid4

from .utils import getRegisteredClient, storeRegisteredClient

clientreg = dict()

class ID4meProvider(Provider):
    id = 'id4me'
    name = 'ID4me'
    account_class = ProviderAccount

    def __init__(self, request):
        super(Provider, self).__init__()
        self._client = None
        if request is not None:
            self._client = self._get_client(request)

    def _get_client(self, request):
        fullurl = request.build_absolute_uri(request.path)
        app_type = 'native' if fullurl.startswith('http://localhost') else 'web'
        try:
            client_config = self.get_app(request)
        except SocialApp.DoesNotExist:
            raise ImproperlyConfigured("No ID4me app configured: please"
                                       " add a SocialApp using the Django"
                                       " admin")
        client_name = client_config.name
        if (app_type, client_name) in clientreg:
            client = clientreg[(app_type, client_name)]
        else:
            returnurl = request.build_absolute_uri(reverse('id4me_callback'))
            client_id = client_config.client_id
            client = ID4meClient(
                validate_url=returnurl,
                app_type=app_type,
                client_name=client_name,
                preferred_client_id=client_id,
                get_client_registration=getRegisteredClient,
                save_client_registration=storeRegisteredClient,
                requireencryption=False
            )
            clientreg[(app_type, client_id)] = client
        return client

    def get_rp_context(self, id4me):
        ctx = self._client.get_rp_context(
            id4me)
        return ctx

    def get_consent_url(self, ctx):
        userinfo_claims = {
            OIDCClaim.name: ID4meClaimRequestProperties(
                essential=True,
                reason='To call you by name'),
            OIDCClaim.given_name: ID4meClaimRequestProperties(
                essential=True,
                reason='To call you by name'),
            OIDCClaim.family_name: ID4meClaimRequestProperties(
                essential=True,
                reason='To call you by name'),
            OIDCClaim.picture: ID4meClaimRequestProperties(
                reason='To display your picture'),
            OIDCClaim.profile: ID4meClaimRequestProperties(
                reason='To display your profile'),
            OIDCClaim.preferred_username: ID4meClaimRequestProperties(
                reason='To assign you wished use name'),
        }

        if QUERY_EMAIL:
            userinfo_claims[OIDCClaim.email] = ID4meClaimRequestProperties(
                essential=EMAIL_REQUIRED,
                reason='To be able to contact you')
            if EMAIL_VERIFICATION:
                userinfo_claims[OIDCClaim.email_verified] = ID4meClaimRequestProperties(
                    essential=True,
                    reason='To know if your E-mail was verified'),


        return self._client.get_consent_url(
            context=ctx,
            claimsrequest=ID4meClaimsRequest(
                userinfo_claims=userinfo_claims
            ),
            usenonce=True,
            state=str(uuid4())
        )

    def get_login_url(self, request, **kwargs):
        url = reverse('id4me_login')
        if kwargs:
            url += '?' + urlencode(kwargs)
        return url

    def get_response(self, context, code):
        id_token = self._client.get_idtoken(context=context, code=code)
        user_info = self._client.get_user_info(context=context)
        return {
            'id_token': id_token,
            'user_info': user_info,
        }

    def extract_extra_data(self, response):
        extra_data = response['user_info']
        # server_settings = \
        #     self.get_server_settings(response.endpoint.server_url)
        # extra_attributes = server_settings.get('extra_attributes', [])
        # for attribute_id, name, _ in extra_attributes:
        #     extra_data[attribute_id] \
        #         = get_value_from_response(response, ax_names=[name])
        return extra_data

    def extract_uid(self, response):
        return "{}+{}".format(response['id_token']['iss'], response['id_token']['sub'])

    def extract_common_fields(self, response):
        first_name = response['user_info'].get(str(OIDCClaim.given_name), '')
        last_name = response['user_info'].get(str(OIDCClaim.family_name), '')
        name = response['user_info'].get(str(OIDCClaim.name), "{} {}".format(first_name, last_name))
        email = response['user_info'].get(str(OIDCClaim.email), '')
        username = response['user_info'].get(str(OIDCClaim.preferred_username)) \
            if str(OIDCClaim.preferred_username) in response['user_info'] \
            else response['id_token'].get('id4me.identifier', self.extract_uid(response))
        picture = response['user_info'].get(str(OIDCClaim.picture), '')
        profile = response['user_info'].get(str(OIDCClaim.profile), '')
        return dict(email=email,
                    first_name=first_name,
                    last_name=last_name,
                    name=name,
                    username=username,
                    picture=picture,
                    profile=profile)


provider_classes = [ID4meProvider]
