import os
import sys

from upvest.tenancy import UpvestTenancyAPI
from upvest.exceptions import InvalidRequest


def add_arguments(parser):
    parser.add_argument(
        "--key",
        "-K",
        type=str,
        help="The API Key ID to use. Also can be loaded by setting the UPVEST_API_KEY environment variable.",
    )
    parser.add_argument(
        "--secret",
        "-S",
        type=str,
        help="The API Key shared secret. Also can be loaded by setting the UPVEST_API_KEY_SECRET environment variable.",
    )
    parser.add_argument(
        "--passphrase",
        "-P",
        type=str,
        help="The API Key passphrase. Also can be loaded by setting the UPVEST_API_KEY_PASSPHRASE environment variable.",
    )
    parser.set_defaults(authtype="app")

    subparsers = parser.add_subparsers(help="commands for an application", title="application commands")

    createuser = subparsers.add_parser("createuser")
    createuser.add_argument("username", type=str, help="The username of the user to create")
    createuser.add_argument("password", type=str, help="The password to set for the user")
    createuser.set_defaults(command="createuser")

    deleteuser = subparsers.add_parser("deleteuser")
    deleteuser.add_argument("username", type=str, help="The username of the user to delete")
    deleteuser.set_defaults(command="deleteuser")

    changepassword = subparsers.add_parser("changepassword")
    changepassword.add_argument("username", type=str, help="The username of the user to change the password for")
    changepassword.add_argument("old_password", type=str, help="The user's current password")
    changepassword.add_argument("new_password", type=str, help="The new password to set")
    changepassword.set_defaults(command="changepassword")

    listusers = subparsers.add_parser("listusers")
    listusers.add_argument("limit", type=int, nargs="?", help="The maximum number of users to list")
    listusers.set_defaults(command="listusers")

    listassets = subparsers.add_parser("listassets")
    listassets.set_defaults(command="listassets")

    deleteall = subparsers.add_parser("deleteallusers")
    deleteall.add_argument(
        "--yes-I-really-want-to-do-this",
        action="store_true",
        default=False,
        required=True,
        help="Enter this flag to really really make sure you want to delete all your users.",
    )
    deleteall.set_defaults(command="deleteallusers")


def _create_user(config):
    username = config.args.username
    password = config.args.password
    if username is None or password is None:
        print("Cannot create a user without specifying the username and password")
        sys.exit(1)

    api = config.get_app_api()
    user = api.users.create(username, password)
    print("User %s created" % user.username)


def _delete_user(config):
    username = config.args.username
    user = config.get_app_api().users.get(username)
    user.delete()
    print("User %s deleted" % username)


def _change_password(config):
    username = config.args.username
    old_password = config.args.old_password
    new_password = config.args.new_password
    user = config.get_app_api().users.get(username)
    try:
        user.update(old_password, new_password)
    except InvalidRequest as e:
        error = e.response.json()
        print(error["error"]["message"])
        sys.exit(1)
    print("Password changed for user %s" % username)


def _delete_all_users(config):
    if not config.args.yes_I_really_want_to_do_this:
        print('The "yes really" flag was not set (see --help) so aborting deletion')
        sys.exit(1)
    count = 0
    for user in config.get_app_api().users.all():
        print("Deleting user %s" % user.username)
        user.delete()
        count += 1
    print("Deleted %d users" % count)


def _list_assets(config):
    triads = []
    api = config.get_app_api()
    for ass in api.assets.all():
        triads.append((ass.symbol, ass.name, ass.id))

    max_symbol = max([len(x[0]) for x in triads])
    max_name = max([len(x[1]) for x in triads])
    format_str = "%%%ds | %%%ds | %%s" % (max_symbol, max_name)
    print(format_str % ("Symbol", "Name", "ID"))
    print(format_str % ("-" * max_symbol, "-" * max_name, "-" * 36))
    for triad in triads:
        print(format_str % triad)


def _list_users(config):
    api = config.get_app_api()
    limit = config.args.limit
    if limit is None:
        for user in api.users.all():
            print(user.username)
    else:
        for user in api.users.list(limit):
            print(user.username)


def handle(config):
    command = getattr(config.args, "command", None)
    if command is None:
        print("No command given")
        sys.exit(1)
    handler = {
        "createuser": _create_user,
        "changepassword": _change_password,
        "deleteuser": _delete_user,
        "deleteallusers": _delete_all_users,
        "listusers": _list_users,
        "listassets": _list_assets,
    }.get(command)
    if handler is None:
        print("unknown command %s" % command)
        sys.exit(1)
    handler(config)


def get_key_piece(args, argname):
    val = getattr(args, argname)
    if argname == "key":
        envvar = "UPVEST_API_KEY"
    else:
        envvar = "UPVEST_API_KEY_%s" % argname.upper()
    if val is None:
        val = os.environ.get(envvar)
    if val is None:
        print("The argument --%s or environment variable %s must be set" % (argname, envvar))
        sys.exit(1)
    return val


def application_api_from_args(args):
    key = get_key_piece(args, "key")
    secret = get_key_piece(args, "secret")
    passphrase = get_key_piece(args, "passphrase")
    return UpvestTenancyAPI(key, secret, passphrase, args.base_url)
