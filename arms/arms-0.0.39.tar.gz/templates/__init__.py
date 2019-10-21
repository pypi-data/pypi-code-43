import requests


def level_list(lang_for_env=None):
    """
    如果lang_for_env is None, 返回lang列表（即不含env_keys）
    如果lang_for_env is not None，返回env_keys
    """
    index_text = requests.get('http://gitlab.parsec.com.cn/qorzj/chiji-tool/raw/master/templates/.index.txt').text
    if lang_for_env is None:
        return [line.split()[0] for line in index_text.splitlines() if line.strip()]
    else:
        for line in index_text.splitlines():
            segs = line.split()
            if segs and segs[0] == lang_for_env:
                return segs[-1].split(',') if len(segs) > 1 else []
        return None


def out_levels():
    return list(set(x.split('-', 1)[0] for x in level_list()))


def inner_levels(prefix):
    return list(set(x.split('-', 1)[-1] for x in level_list() if x.startswith(prefix + '-')))
