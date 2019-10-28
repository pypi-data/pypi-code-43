import sys

# Tmux misinterprets 0-count movements as 1-count movements
# (for insance, 0A as 1A), so we return an empty string for no-ops.
up =         lambda n: n and f'\033[{n}A' or ''
down =       lambda n: n and f'\033[{n}B' or ''
right =      lambda n: n and f'\033[{n}C' or ''
left =       lambda n: n and f'\033[{n}D' or ''

horizontal = lambda x: f'\033[{x}G'

erase_line = lambda n: f'\033[{n}K'

grey = lambda s: f'\033[38;5;8m{s}\033[0m'
red = lambda s: f'\033[38;5;9m{s}\033[0m'
green = lambda s: f'\033[38;5;10m{s}\033[0m'
bold = lambda s: f'\033[38;1m{s}\033[0m'

class ManagedLines():
    def __init__(self, keys_as_prefixes=False, prefix_separator=': '):
        self.line_numbers = dict()
        self.items = dict()
        self.keys_as_prefixes = keys_as_prefixes
        self.prefix_separator = prefix_separator
        self.num_lines_managed = 0

    def __setitem__(self, line_key, line_value):
        existing_line_number = self.line_numbers.get(line_key, -1)

        if self.line_numbers:
            highest_line_number = max(self.line_numbers.values())
        else:
            highest_line_number = -1

        if existing_line_number == -1:
            if self.line_numbers:
                print()
            self.num_lines_managed += 1
            self.line_numbers[line_key] = highest_line_number + 1
            lines_back = 0
        else:
            lines_back = self.num_lines_managed - 1 - existing_line_number

        self.items[line_key] = line_value

        if self.keys_as_prefixes:
            new_line_text = f'{line_key}{self.prefix_separator}{line_value}'
        else:
            new_line_text = f'{line_value}'
        print(f'{up(lines_back)}{horizontal(1)}{erase_line(2)}{new_line_text}{down(lines_back)}', end='')
        sys.stdout.flush()

    def __getitem__(self, line_key):
        return self.items[line_key]

    def __delitem__(self, line_key):
        line_number_to_be_deleted = self.line_numbers.get(line_key)
        if not line_number_to_be_deleted:
            return
        lines_back = self.num_lines_managed - 1 - line_number_to_be_deleted
        print(up(lines_back), end='')
        for line_key, existing_line_number in sorted(self.line_numbers.items(), key=lambda e: e[1])[line_number_to_be_deleted+1:]:
            self.line_numbers[line_key] = existing_line_number -1
            line_value = self.items[line_key]
            if self.keys_as_prefixes:
                new_line_text = f'{line_key}{self.prefix_separator}{line_value}'
            else:
                new_line_text = f'{line_value}'
            print(f'{horizontal(1)}{erase_line(2)}{new_line_text}{down(1)}', end='')
        print(f'{horizontal(1)}{erase_line(2)}', end='')
        sys.stdout.flush()


    def get(self, line_key, default=''):
        if line_key in self.keys():
            return self[line_key]
        else:
            return default

    def keys(self):
        return self.line_numbers.keys()

    def done(self):
        print()

    # done() makes sure the cursor is on a new line below the managed lines.
    # Implementing __del__() means that you can use ManagedLines like this:
    # lines = ManagedLines()
    # lines['foo'] = 42
    # del lines

    def __del__(self):
        self.done()

    # __enter__() and __exit__() implement a context manager. ManagedLines can be used like this:
    # with ManagedLines() as lines:
    #     lines['foo'] = 42

    def __enter__(self):
        return self

    def __exit__(self, *a):
        self.done()
        return False

