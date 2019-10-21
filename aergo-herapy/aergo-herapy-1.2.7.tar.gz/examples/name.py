import sys
import traceback
import time

import aergo.herapy as herapy


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)
    print(*args, **kwargs)


def run():
    try:
        aergo = herapy.Aergo()

        print("------ Connect AERGO -----------")
        aergo.connect('localhost:7845')

        exp_acc = "47eY3XwQ2UgjNfWCXhhySwmZNvrFf3MASEE6hdqxdG5ioQPWKsVNdZyecFqbCVt752ANPAUpY"
        password = "1234"

        aergo.import_account(exported_data=exp_acc, password=password)
        print(str(aergo.account.address))

        rs = aergo.get_name_info(name="te0123456789")
        print(rs.name)
        print(rs)

        print("------ Disconnect AERGO -----------")
        aergo.disconnect()
    except Exception as e:
        eprint(e)
        traceback.print_exception(*sys.exc_info())


if __name__ == '__main__':
    run()
