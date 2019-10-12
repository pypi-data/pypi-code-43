# python3 -m ask4args model:function
import importlib
import sys
from .core import Ask4Args, Ask4ArgsGUI, Ask4ArgsWeb


def main():
    function = None
    classes = (Ask4Args, Ask4ArgsGUI, Ask4ArgsWeb)
    for arg in sys.argv[1:]:
        if arg.count(':') != 1:
            continue
        module_name, func_name = arg.split(':')
        mod = importlib.import_module(module_name)
        function = getattr(mod, func_name, None)
        if function is None:
            raise ValueError(
                f'no function named {func_name} in module {module_name}')
    choices = '\n'.join(
        [f'{num}. {cls.__name__}' for num, cls in enumerate(classes, 1)])
    choice = int(input(f'Choose the UI class number:\n{choices}\n') or 1)
    cls = classes[choice - 1]
    cls(function).run()


if __name__ == "__main__":
    main()
