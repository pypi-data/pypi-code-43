import logging
from mpipes.common import str2bool
from mpipes.common_auth import *

from cliff.command import Command
from cliff.lister import Lister
from cliff.show import ShowOne


class AuthDefault(Command):
    'Set authentication as default'

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(AuthDefault, self).get_parser(prog_name)
        parser.add_argument('authentication', type=str, help='Authentication to select as default', nargs=1)
        return parser

    def take_action(self, parsed_args):
        set_default_authentication(parsed_args.authentication[0])

class AuthList(Lister):
    'List authentications'

    log = logging.getLogger(__name__)


    def list_auths(self):
        basedir = base_dir()
        rt = []
        for f in os.listdir(basedir):
            if f.endswith(AUTH_FILE_SUFFIX):
                rt.append(os.path.splitext(f)[0])
        return rt

    def take_action(self, parsed_args):
        headers = ['authentication', 'is_default']
        rt = []
        default_auth = get_default_authentication()
        for au in self.list_auths():
            rt.append( (au, au == default_auth ))
        return headers, rt

class AuthAuthenticate(Command):
    'Authenticate and store authentication info for other commands'

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(AuthAuthenticate, self).get_parser(prog_name)
        parser.add_argument("--auth_domain", type=str, help='Auth0 domain', default='optimaideas.eu.auth0.com')
        parser.add_argument("--auth_client_id", type=str, help='Auth0 client id (build-in id of this cli app)',
                          default='tJV1YtC1baTq3i8Tn0Eyq6kF37PiAsfd')
        parser.add_argument("--auth_api_identifier", type=str, help='Identifier of this api (for different deployment types)',
                          default='https://dev.micropipes.optimaideas.com/')
        parser.add_argument("--micropipes_domain", type=str, help='Domain where api is running (without http/https prefix)', required=True)
        parser.add_argument("--micropipes_port", type=int, help='Port where api is running', default=-1)
        parser.add_argument("--https", type=str2bool, nargs='?',
                            const=True, default=False,
                            help="Use https")
        parser.add_argument("--set_default", type=str2bool, nargs='?',
                            const=True, default=False,
                            help="If success set as default auth")
        return parser

    def take_action(self, parsed_args):
        user_token_device_auth(parsed_args)


class AuthInfo(ShowOne):
    'Show authentication info'

    log = logging.getLogger(__name__)

    def get_parser(self, prog_name):
        parser = super(AuthInfo, self).get_parser(prog_name)
        parser.add_argument('authentication', type=str, help='Authentication to show', nargs=1)
        return parser

    def take_action(self, parsed_args):
        columns = (
            'domain', 'http(s) port', 'https',
            'issued at', 'expires in',
            'api_identifier', 'auth_domain', 'client_id', 'has refresh_token',
            'http://optimaideas.com/user_id', 'permissions',
            'nickname', 'email'
        )
        data = load_authentication_data(parsed_args.authentication[0])
        uinfo = validate_access_token(data['api_identifier'], data['auth_domain'], data['access_token'])
        # print(uinfo)
        userinfo = get_user_info(data['auth_domain'], data['access_token'])
        # print(userinfo)
        if userinfo:
            userinfo = json.loads(userinfo)

        rdata = ()
        if data:
            rdata = (
                data['micropipes_domain'],
                data['micropipes_port'],
                data['https'],
                datetime.fromtimestamp(data['issued']),
                datetime.fromtimestamp(data['issued'] + data['expires_in']),
                data['api_identifier'],
                data['auth_domain'],
                data['client_id'],
                'refresh_token' in data,
                None if (not uinfo or not 'http://optimaideas.com/user_id' in uinfo ) else uinfo[
                    'http://optimaideas.com/user_id'],
                None if (not uinfo or not 'permissions' in uinfo) else uinfo[
                    'permissions'],
                None if (not userinfo or not 'nickname' in userinfo) else userinfo['nickname'],
                None if (not userinfo or not 'email' in userinfo) else userinfo['email'],
            )
        return (columns, rdata)