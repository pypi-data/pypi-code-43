"""Module which generates contents of BUILD and WORKSPACE files for Bazel."""

import string
import typing


def generate_build_template(name: str, sources: typing.List[str]) -> str:
    """Return the content for BUILD file for given Python module.

    Args:
        name (str): Name of the Python module.
        sources (:obj:`list` of :obj:`str`): List of source paths for the
        module.

    Returns:
        str: Content for the BUILD file.

    """
    build_template = string.Template("""py_library(
    name = "${name}",
    srcs = ${sources},
    visibility = ["//visibility:public"],
)
""")
    str_sources = "glob([{}])".format(", ".join(f'"{src}"' for src in sources))
    return build_template.substitute({"name": name, "sources": str_sources})


def generate_workspace_template(name: str) -> str:
    """Return the content for WORKSPACE file for given Python module.

    Args:
        name (str): Name of the Python module.

    Returns:
        str: Content for the WORKSPACE file.

    """
    workspace_template = string.Template("""workspace(name = "${name}")
""")
    return workspace_template.substitute({"name": name})
