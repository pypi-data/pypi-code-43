"""Unit tests for the bazel_workspaces_python.template module."""

from bazel_workspaces_python import template


def test_generate_build_template():
    """Test for the generate_build_template function."""
    tests = (
        (
            "markupsafe",
            ["/usr/lib64/python3.6/site-packages/markupsafe/**/*.py"],
            """py_library(
    name = "markupsafe",
    srcs = glob(["/usr/lib64/python3.6/site-packages/markupsafe/**/*.py"]),
    visibility = ["//visibility:public"],
)
"""),
        (
            "jinja2",
            ["/usr/lib/python3.6/site-packages/jinja2/**/*.py"],
            """py_library(
    name = "jinja2",
    srcs = glob(["/usr/lib/python3.6/site-packages/jinja2/**/*.py"]),
    visibility = ["//visibility:public"],
)
"""),
    )
    for name, sources, expected in tests:
        build_content = template.generate_build_template(name, sources)
        assert build_content == expected


def test_generate_workspace_template():
    """Test for the generate_workspace_template function."""
    tests = (
        ("markupsafe", """workspace(name = "markupsafe")
"""),
        ("jinja2", """workspace(name = "jinja2")
"""),
    )
    for name, expected in tests:
        workspace_content = template.generate_workspace_template(name)
        assert workspace_content == expected
