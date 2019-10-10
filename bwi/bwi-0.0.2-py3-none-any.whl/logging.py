import os


def debug(text: str):
    # FIXME: Send to a queue when we are on BWI Infra
    if os.environ.get('BWI_INFRA') is not None:
        print("On infra : ", text)
    else:
        print(text)


def info(text: str):
    # FIXME: Send to a queue when we are on BWI Infra
    if os.environ.get('BWI_INFRA') is not None:
        print("On infra : ", text)
    else:
        print(text)


def warning(text: str):
    # FIXME: Send to a queue when we are on BWI Infra
    if os.environ.get('BWI_INFRA') is not None:
        print("On infra : ", text)
    else:
        print(text)


def error(text: str):
    # FIXME: Send to a queue when we are on BWI Infra
    if os.environ.get('BWI_INFRA') is not None:
        print("On infra : ", text)
    else:
        print(text)
