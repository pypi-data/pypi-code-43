from . import licenses


def init(license_type):
    license = license_type.replace('/', '-')
    file = "{}.txt".format(license)

    content = license
    try:
        content = licenses(file)
    except:
        pass

    return content