import sys


def add_arguments(parser):
    parser.add_argument(
        "--client-id",
        "-C",
        type=str,
        help="The OAuth Client ID used to authenticate individual users. Also can be loaded by setting the UPVEST_OAUTH_CLIENT_ID environment variable.",
    )
    parser.add_argument(
        "--client-secret",
        "-O",
        type=str,
        help="The OAuth Client secret used to authenticate individual users. Also can be loaded by setting the UPVEST_OAUTH_CLIENT_SECRET environment variable.",
    )
    parser.add_argument(
        "--login",
        "-l",
        type=str,
        help="The username of the user. Also can be loaded by setting the UPVEST_USERNAME environment variable.",
    )
    parser.add_argument(
        "--password",
        "-w",
        type=str,
        help="The password of the user. Also can be loaded by setting the UPVEST_PASSWORD environment variable.",
    )
    parser.set_defaults(authtype="user")

    subparsers = parser.add_subparsers(help="commands for a user", title="user commands")

    createwallet = subparsers.add_parser("createwallet")
    createwallet.add_argument("assetid", nargs="+", help="The ID of the asset or assets to create a wallet for")
    createwallet.set_defaults(command="createwallet")

    listwallets = subparsers.add_parser("listwallets")
    listwallets.set_defaults(command="listwallets")

    listtransactions = subparsers.add_parser("listtransactions")
    listtransactions.add_argument("walletid", type=str, help="The ID of the wallet to list transactions for")
    listtransactions.set_defaults(command="listtransactions")

    send = subparsers.add_parser("send")
    send.add_argument("walletid", type=str, help="Which wallet to send from")
    send.add_argument("assetid", type=str, help="Which asset type to send")
    send.add_argument("quantity", type=int, help="How much to send")
    send.add_argument("fee", type=int, help="How much to pay for the transaction")
    send.add_argument("recipient", type=str, help="Which address to send to")
    send.set_defaults(command="send")


def _create_wallet(config):
    wallets = [config.get_user_api().wallets.create(asset_id, config.args.password) for asset_id in config.args.assetid]
    for wallet in wallets:
        print(wallet.id, wallet.address)
        for balance in wallet.balances:
            print("    ", balance["asset_id"], balance["name"], balance["amount"], "10^%d" % balance["exponent"])


def _list_wallets(config):
    for wallet in config.get_user_api().wallets.all():
        print(wallet.id, wallet.address)
        for balance in wallet.balances:
            print("    ", balance["asset_id"], balance["name"], balance["amount"], "10^%d" % balance["exponent"])


def _list_transactions(config):
    wallet = config.get_user_api().wallets.get(config.args.walletid)
    for tx in wallet.transactions.all():
        print(tx.txhash, tx.status, tx.quantity, tx.fee, tx.sender)


def _create_transaction(config):
    api = config.get_user_api()
    wallet = api.wallets.get(config.args.walletid)
    tx = wallet.transactions.create(
        config.args.password, config.args.assetid, config.args.quantity, config.args.fee, config.args.recipient
    )
    print("Transaction successfully created: %s" % tx.txhash)


def handle(config):
    command = getattr(config.args, "command", None)
    if command is None:
        print("No command given")
        sys.exit(1)
    handler = {
        "createwallet": _create_wallet,
        "listtransactions": _list_transactions,
        "send": _create_transaction,
        "listwallets": _list_wallets,
    }.get(command)
    if handler is None:
        print("unknown command %s" % command)
        sys.exit(1)
    handler(config)
