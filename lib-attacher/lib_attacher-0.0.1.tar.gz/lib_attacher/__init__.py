import os
import sys

def attach_folder_in_hierarchy(start_folder:str, target_sub_path:str, extra_sub_path:str) -> str:
    '''
    This is exactly like search_folder_hierarchy.  If a path is returned as output, it will have been appended to the
    module search path via:
        sys.path.insert(0, output)
    '''

    folder = search_folder_hierarchy(start_folder, target_sub_path, extra_sub_path)

    if folder is not None:
        sys.path.insert(0,folder)

    return folder


def search_folder_hierarchy(start_folder:str, target_sub_path:str, extra_sub_path:str=None) -> str:
    '''
    Searches the hierarchy above `start_folder` for a `target_sub_path`.  For example, suppose the caller passes
    in the following arguments.
        start_folder = "/a/b/c/d"
        target_sub_path = "w/x"
        extra_sub_path = "y/z

    This method will find the first of the following paths which exist (from top to bottom).

        /a/b/c/d/w/x/y/z
        /a/b/c/w/x/y/z
        /a/b/w/x/y/z
        /a/w/x/y/z
        /w/x/y/z

    If one of the paths exist, the method will return that path, but without the extra_sub_path.  For example, if the
    path "/a/b/c/w/x/y/z" is the one which is found, this method will only return "a/b/c/w/x".

    If none of the paths above exist, then the method will return None.

    :param start_folder: An absolute path to a folder on the system.
    :param target_sub_path: A relative sub path which you are searching for.
    :return: The name of the path, if found; or None.
    '''

    if start_folder is None:
        raise Exception(f"The {start_folder.__name__} is None.")
    if target_sub_path is None:
        raise Exception(f"The {target_sub_path.__name__} is None.")

    if not os.path.isabs(start_folder):
        raise Exception(f"The {start_folder.__name__} is not an absolute path:  {start_folder}")

    if os.path.isabs(target_sub_path):
        raise Exception(f"The {target_sub_path.__name__} is an absolute path:  {start_folder}")

    try_folder = start_folder
    while try_folder != None:

        if extra_sub_path != None:
            try_target_path = os.path.join(try_folder, target_sub_path, extra_sub_path)
        else:
            try_target_path = os.path.join(try_folder, target_sub_path)

        if os.path.exists(try_target_path):
            # success -- we found it
            return os.path.join(try_folder, target_sub_path)
        last_try_folder = try_folder
        try_folder = os.path.dirname(try_folder)

        if try_folder == last_try_folder:
            # fail -- the path has no parents
            break

    return None