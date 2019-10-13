import sys

def subargs(sys_args):
    def wrapper(func):
        def _args(*args, **kwargs):
            args = sys_args

            if len(args) < 2:
                return func(*args, **kwargs)

            command = args[1]

            if 'new' == command:
                if len(args) <= 2 or args[2] in \
                    ['--django', '--quick', '--venv', '--virtualenv']:
                    raise ValueError('Project name must be provided.')
                else:
                    kwargs['project_name'] = args[2]
                    args.remove(kwargs['project_name'])
            elif 'install' == command:
                if len(args) > 2:
                    no_add_index = len(args)
                    if '--no-add' in args:
                        no_add_index = args.index('--no-add')
                    kwargs['packages'] = args[2:no_add_index]

                    if no_add_index < len(args):
                        args[2] = '--no-add'
                        args[3:] = []
                    else:
                        args[2:] = []

            elif 'remove' == command or 'add' == command:
                if len(args) < 3:
                    sys.stdout.write('No package(s) provided.')
                    return
                else:
                    kwargs['packages'] = args[2:]
                    args = args[:2]
            elif 'module' == command:
                if len(args) < 3 or args[2] == '--add' or '--parentmodule' in args[2]:
                    sys.stdout.write('No module name provided.')
                    return

                if '--add' in args and not args[args.index('--add') + 1:]:
                    raise ValueError('At least one file name must be given.')

                if '--add' in args:
                   kwargs['selected_files'] = args[args.index('--add') + 1:]
                   args = args[:args.index('--add') + 1]

                kwargs['module_name'] = args[2]
                kwargs['parent_module'] = args[3].split('=')[1] if len(args) > 3 and '--parentmodule' in args[3] else ""
                args.remove(kwargs['module_name'])

            return func(*args, **kwargs)
        return _args
    return wrapper
