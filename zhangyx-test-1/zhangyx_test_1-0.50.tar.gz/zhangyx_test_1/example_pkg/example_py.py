def get_sum():
    sum = 0
    for i in range(1, 101):
        sum += i
    return sum


def print_example():

    print("import example_py.py successful!")


if __name__ == "__main__":
    ans = get_sum()
    print('The sum of 1~100 is: ' + str(ans))
    print_example()
