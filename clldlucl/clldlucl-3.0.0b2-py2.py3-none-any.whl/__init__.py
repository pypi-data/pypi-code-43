from pyramid.response import Response

from clld.interfaces import IOlacConfig
from clld.web.views.olac import OlacConfig, Participant, Institution


class MpgOlacConfig(OlacConfig):
    def admin(self, req):
        return Participant("Admin", "Gereon A. Kaiping", "g.a.kaiping@hum.leidenuniv.nl")

    def description(self, req):
        res = OlacConfig.description(self, req)
        res['institution'] = Institution(
            'Leiden University Centre for Linguistics',
            'https://www.universiteitleiden.nl/en/humanities/leiden-university-centre-for-linguistics',
            'Leiden, The Netherlands')
        return res


def includeme(config):
    config.include('clld.web.app')
    config.registry.registerUtility(MpgOlacConfig(), IOlacConfig)
    config.add_static_view('clldlucl-static', 'clldlucl:static')
    config.add_settings({'clld.publisher_logo': 'clldlucl:static/lucl.png'})
    config.add_settings(
        {'clld.privacy_policy_url': 'https://www.shh.mpg.de/138116/privacy-policy'})
    config.add_route('google-site-verification', 'googlebbc8f4da1abdc58b.html')
    config.add_view(
        lambda r: Response('google-site-verification: googlebbc8f4da1abdc58b.html'),
        route_name='google-site-verification')
