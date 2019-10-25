import six
import getpass


def remove_newlines(text):
    return text.replace('\n', '')


def remove_non_ascii(text):
    return ''.join([x if ord(x) < 128 else '' for x in text])


def replace_non_asci_with_underscore(text):
    return ''.join([x if x.isalnum() else '_' for x in text])


def add_dottorrent(text):
    return '{}.torrent'.format(text)


def to_bytes(text):
    if six.PY2:
        try:
            text = text.encode('utf-8')
        except AttributeError:
            pass
    if six.PY3:
        try:
            text = text.encode()
        except AttributeError:
            pass
    return text


def unicode_cast(obj):
    try:
        return obj.decode('utf-8')
    except AttributeError:
        return obj


def py3_unicode(text):
    if six.PY3:
        try:
            return text.decode('unicode_escape')
        except AttributeError:
            pass
    return text


def py3_to_bytes(text):
    if six.PY3:
        return bytearray(text, encoding='utf-8')
    return text


def hidden_prompt(message='Password'):
    pass1 = 0
    pass2 = 1
    while pass1 != pass2:
        pass1 = getpass.getpass('Enter {}: '.format(message))
        pass2 = getpass.getpass('Confirm {}: '.format(message))

        if pass1 != pass2:
            print("\n{} don't match, try again...\n".format(message))
    return pass1


def prompt(message, test_value=None):
    """
    Deal with python2 python3 input differences and use hidden input field for password like inputs
    """
    if test_value:
        return test_value

    passfields = ['S3 access IAM Secret Key', 'database password']
    if message in passfields or 'assword' in message.lower() or 'secret' in message.lower():
        return hidden_prompt('%s: ' % message)
    else:
        return input('%s: ' % message)


def python3_decode_utf8(text):
    try:
        text = text.decode('utf-8')
    except AttributeError:
        pass
    return text
