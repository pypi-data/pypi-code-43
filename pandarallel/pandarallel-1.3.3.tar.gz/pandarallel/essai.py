toto = 4


def main():
    dum = """def titi(x, y):
        print(toto)
        return x + y
    """

    exec(dum)

    # print("GLOBALS")
    # print(globals())
    # print()
    # print("LOCALS")
    # print(locals())
    print(locals()['titi'](5, 6))


if __name__ == "__main__":
    main()
