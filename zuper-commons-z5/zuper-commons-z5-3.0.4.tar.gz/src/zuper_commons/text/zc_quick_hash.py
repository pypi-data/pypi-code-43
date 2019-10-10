from typing import Union


__all__ = ["get_md5", "get_sha1"]


def get_md5(contents: Union[bytes, str]) -> str:
    """ Returns an hexdigest (string).
        If the contents is a string, then it is encoded as utf-8.
    """
    if isinstance(contents, str):
        contents = contents.encode("utf-8")
    from zuper_commons.types import check_isinstance

    check_isinstance(contents, bytes)
    import hashlib

    m = hashlib.md5()
    m.update(contents)
    s = m.hexdigest()
    check_isinstance(s, str)
    return s


def get_sha1(contents: bytes) -> str:
    """ Returns an hexdigest (string) """
    from zuper_commons.types import check_isinstance
    import hashlib

    check_isinstance(contents, bytes)
    m = hashlib.sha1()
    m.update(contents)
    s = m.hexdigest()
    check_isinstance(s, str)
    return s
