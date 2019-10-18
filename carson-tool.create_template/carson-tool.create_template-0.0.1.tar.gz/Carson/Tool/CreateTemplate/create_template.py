import colorama
from colorama.ansi import AnsiFore
from colorama import Fore, Back

from pathlib import Path
from os import startfile

SCRIPT_DIR = Path(__file__).resolve().parent
TEMPLATE_DIR = SCRIPT_DIR.joinpath('template')


def highlight_print(msg: str, fore_color: AnsiFore = Fore.RED) -> None:
    print(Back.LIGHTYELLOW_EX + fore_color + msg)


def main(args):
    template_file = TEMPLATE_DIR / f'{args.ref}.template'
    if not template_file.exists():
        raise FileNotFoundError(template_file)

    template_text = template_file.read_text()
    work_dir = Path('.')  # current command line path
    outfile = work_dir / args.new_file_name
    outfile.write_text(template_text)
    startfile(work_dir)


if __name__ == '__main__':
    colorama.init(autoreset=True)

    from argparse import ArgumentParser

    arg_parser = ArgumentParser()
    arg_parser.add_argument("ref", help="ref template")
    arg_parser.add_argument("new_file_name", help="new file name")

    g_args = arg_parser.parse_args()
    highlight_print('GLOBAL ARGUMENT PARSER')
    print(f"{'key':<20} {'value':<40}")
    for key, value in vars(g_args).items():
        print(f"{key:<20} {value if value is not None else '':<40}")
    main(g_args)
