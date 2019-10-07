def __clean_start_end_slashes(s):
    if s.endswith("/"): s = s[:-1]
    if s.startswith("/"): s = s[1:]
    return s

def url_join(path, *paths):
    all_paths = [path] + list(paths)
    return "/".join(map(__clean_start_end_slashes, filter(lambda x: x, all_paths)))