from typing import List


def error_path_not_is_document(path: List[str], message=""):
    return Exception("Error PATH not is Document -> {} | {}".format(".".join(path), message))


def error_path_not_is_collection(path: List[str], message=""):
    return Exception("Error PATH not is Document -> {} | {}".format(".".join(path), message))

