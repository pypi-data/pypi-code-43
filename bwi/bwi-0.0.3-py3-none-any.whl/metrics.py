import os


def inc(name: str, value: int):
    # FIXME: Send to a queue when we are on BWI Infra
    if os.environ.get('BWI_INFRA') is not None:
        print("On infra : ", name, value)
    else:
        print(name, value)


def dec(name: str, value: int):
    # FIXME: Send to a queue when we are on BWI Infra
    if os.environ.get('BWI_INFRA') is not None:
        print("On infra : ", name, value)
    else:
        print(name, value)


def value(name: str, value: int):
    # FIXME: Send to a queue when we are on BWI Infra
    if os.environ.get('BWI_INFRA') is not None:
        print("On infra : ", name, value)
    else:
        print(name, value)
