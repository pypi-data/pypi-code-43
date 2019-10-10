import importlib
import pkgutil
from jiratag_commitizen.cz.conventional_commits import ConventionalCommitsCz
from jiratag_commitizen.cz.jira import JiraSmartCz

registry = {"cz_conventional_commits": ConventionalCommitsCz, "cz_jira": JiraSmartCz}
plugins = {
    name: importlib.import_module(name).discover_this
    for finder, name, ispkg in pkgutil.iter_modules()
    if name.startswith("cz_")
}

registry.update(plugins)
