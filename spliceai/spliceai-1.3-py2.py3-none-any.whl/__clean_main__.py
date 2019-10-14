from spliceai.__main__ import main


def clean_main():

    try:
        main()
    except KeyboardInterrupt:
        exit(0)
