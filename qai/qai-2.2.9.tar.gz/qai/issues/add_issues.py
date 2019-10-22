from qai.qconnect.qallback import qallback


def parse_old_format(el):
    segment = el["data"]["content"]["segment"]
    metadata = el["data"]["meta"]
    language = el["data"]["content"]["languageCode"].split("-")[0]
    return segment, metadata, language


def parse_new_format(el):
    segment = el["content"]["segment"]
    metadata = el["meta"]
    language = el["content"]["languageCode"].split("-")[0]
    return segment, metadata, language


def add_issues_to_new_format(el, issues):
    el["issues"] = issues
    return el


def add_issues_to_old_format(el, issues):
    el["data"]["issues"] = issues
    return el


def add_issues_format_insensitive(instance, el):
    # We should pull some of this code out soon
    # Why write it then? because I don't trust the calling services
    # to do what Yakiv says will happen
    try:
        segment, metadata, language = parse_new_format(el)
        new_format = True
    except KeyError:
        print("could not parse in new format, trying old format")
        segment, metadata, language = parse_old_format(el)
        new_format = False
    # try except in case of unforseen problems
    try:
        issues = qallback(instance, segment, metadata, language)
    except:
        print(f"Error log for segment {segment}")
        issues = []
    finally:
        if new_format:
            el = add_issues_to_new_format(el, issues)
        else:
            el = add_issues_to_old_format(el, issues)
    return el
