__version__ = "0.0.3"


def setup(app):
    """Initialize Sphinx extension."""
    import sphinx
    from .parser import JinjaMarkdownParser, JinjaRestructuredTextParser

    if sphinx.version_info >= (1, 8):
        app.add_source_suffix(".jrst", "jrst")
        app.add_source_parser(JinjaRestructuredTextParser)
        if JinjaMarkdownParser is not None:
            app.add_source_suffix(".jmd", "jmarkdown")
            app.add_source_suffix(".jmarkdown", "jmarkdown")
            app.add_source_parser(JinjaMarkdownParser)
    elif sphinx.version_info >= (1, 4):
        app.add_source_parser(".jrst", JinjaRestructuredTextParser)
        if JinjaMarkdownParser is not None:
            app.add_source_parser(".jmd", JinjaMarkdownParser)

    return {"version": __version__, "parallel_read_safe": True}
