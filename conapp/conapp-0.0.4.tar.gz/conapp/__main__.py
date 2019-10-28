import sys

from conapp.arguments import get_args
from conapp.file_paths import check_dirs, create_dirs


def main() -> None:
    args = get_args(sys.argv[1:])

    if not check_dirs():
        print("creating config dirs...")
        create_dirs()

    args.command(args)


if __name__ == "__main__":
    main()
