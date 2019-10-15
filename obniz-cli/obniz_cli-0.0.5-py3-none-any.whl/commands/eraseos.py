import sys
import subprocess

from . import util

def command(args):
    if args.port:
        selected_port = args.port
    else:
        selected_port = util.select_port()
    
    print()
    repl = input("Erase entire flash chip?(y/n):")
    while repl.lower() not in ["y", "n"]:
        repl = input("Erase entire flash chip?(y/n):")
    if repl.lower() == "n":
        print("Canceled.")
        sys.exit(0)
    elif repl.lower() == "y":
        pass

    print()
    proc = subprocess.run(
        "esptool.py --port {} erase_flash".format(selected_port),
        shell=True
    )