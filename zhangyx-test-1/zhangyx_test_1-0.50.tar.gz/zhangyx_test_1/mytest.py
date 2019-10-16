import sys
from zhangyx_test_1.example_pkg.example_py import get_sum, print_example

def get():
    return sys.path


if __name__ == "__main__":
    print(get_sum())
    print_example()
