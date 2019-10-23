import argparse


def get_configure_path_from_argv(args=None):
    parser = argparse.ArgumentParser()
    parser.add_argument('--ioflow_default_configure', type=str, nargs='?', help='specific default configure file location')

    args, unknown = parser.parse_known_args(args)

    print("+" * 8, "Unknown argvs", '+' * 8)
    print(unknown)

    return args.ioflow_default_configure


if __name__ == "__main__":
    config = get_configure_path_from_argv(args="--ioflow_default_configure xx --aaa --bb -c".split())
    print(config)