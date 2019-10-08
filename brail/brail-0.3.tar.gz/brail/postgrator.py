import re
from .git import list_tree

POSTGRATOR_FWD_MIGRATION_REGEX = re.compile(r'^([0-9]+)\.do.*\.sql$')

def list_postgrator_records(conf, treeish):
    if conf['postgrator_dir'] is None:
        return []
    postgrator_dir = conf['postgrator_dir']
    return [
        'pg/' + x
        for x in list_tree(treeish, postgrator_dir + '/')
        if POSTGRATOR_FWD_MIGRATION_REGEX.match(x) is not None
    ]
