"""Project specific sphinx extension to document click commands.

Adds the directive ``click-cmd`` and a corresponding role allowing the automatic
documentation of a command line interface implemented through click_. Have a look at
:class:`ClickCmdDirective` for usage information.

Make sure this module can be imported by sphinx either by installation or by appending
its directory to Python's PATH.

.. _click: https://click.palletsprojects.com
"""


from math import inf
from importlib import import_module

import click
from docutils.parsers.rst import directives, nodes
from docutils.statemachine import StringList
from sphinx import addnodes
from sphinx.directives import SphinxDirective
from sphinx.domains import ObjType
from sphinx.roles import XRefRole
from sphinx.util import logging


logger = logging.getLogger(__name__)


class ClickCmdDirective(SphinxDirective):
    """Directive to automatically document a click.Command.

    This directive works similar to the ``auto...::`` directives provided by the
    autodoc module but for commands implemented with the library click. The directive
    expects one argument that consists of the module path and the function name of the
    command that should be documented. E.g. to document a function named ``foo`` inside
    the module ``bar.baz`` you would write::

        .. click-cmd:: bar.baz:foo

    The directive has following options:

    - ``name``: A string which will override the displayed name of the command. This is
      useful if the command implicitly relies on click to find the correct program name
      which won't work when using this directive. Instead of guessing, the user should
      then set the explicit name him- or herself.
    - ``prefix``: This string will be prepended to the command name. Useful when
      documenting subcommands separately in which case name of the parent command is
      unknown.
    - ``subcommands``: If this flag is provided, available subcommands will be shown in
      a table below the options.
    - ``maxdepth``: The directive can fully document subcommands as well. This option
      controls the depth by which the subcommand tree is traversed. The tree is fully
      traversed by default. Use 0 to document only the current command.
    - ``linkcode``: This works similar to the sphinx.ext.linkcode_ extension. For this
      to work the function ``click_cmd_resolve`` must be defined inside `conf.py`. This
      function must produce an url for the input
      (``domain="std"``, ``info={"module": "...", "fullname": "..."}``).

    .. _sphinx.ext.linkcode:
       http://www.sphinx-doc.org/en/master/usage/extensions/linkcode.html

    See Also
    --------
    `sphinx-click <https://github.com/click-contrib/sphinx-click>`_
        An alternative for documenting CLIs created with click.
    """

    required_arguments = 1
    option_spec = {
        "name": directives.unchanged,
        "prefix": directives.unchanged,
        "subcommands": directives.flag,
        "maxdepth": directives.nonnegative_int,
        "linkcode": directives.flag,
    }
    has_content = False

    domain = None
    object_type = None
    location = None
    resolve_target = None

    def import_command(self, signature):
        """Import a click.Command based on the signature.

        Parameters
        ----------
        signature : str
            Signature of the directive with the format "<module_path>:<function_name>".

        Returns
        -------
        command : click.Command or click.Group
            The imported command.
        """
        if ":" not in signature:
            raise ValueError(
                "must contain a ':' separating module path and function name"
            )
        module_path, function_name = signature.split(":")
        module = import_module(module_path)
        command = getattr(module, function_name)
        return command

    def format_help(self, ctx):
        """Extract and format help message for a command.

        Parameters
        ----------
        ctx : click.Context
            Context with the command.

        Yields
        ------
        line : str
            The next line in the formatted help message.
        """
        cmd = ctx.command

        # Write help text. click assigns special meaning to the characters \f and \b
        help_text = cmd.help.split("\f")[0]  # skip content after \f
        prefix = ""
        for line in help_text.splitlines():
            if "\b" in line:
                # Start literal block
                yield from ["::", ""]
                prefix = "   "  # Indent paragraph following a \b
            elif line == "":
                prefix = ""  # but reset for next paragraph
                yield ""
            else:
                yield prefix + line

        def rst_list_table(rows):
            """Format `rows` as simple RST list-table."""
            yield from (".. list-table::", "")
            for row in rows:
                for i, item in enumerate(row):
                    if i == 0:
                        yield f"   - * {item}"
                    else:
                        yield f"     * {item}"

        # Prepare the option section
        options = (p for p in cmd.get_params(ctx) if isinstance(p, click.Option))
        options = (o.get_help_record(ctx) for o in options)
        options = [(f"``{signature}``", descr) for signature, descr in options]
        # and yield the content
        yield from ["", ".. rubric:: Options", ""]
        yield from rst_list_table(options)

        # Document potential subcommands if option was provided
        if "subcommands" in self.options and hasattr(cmd, "commands"):
            template = f":click-cmd:`{ctx.command_path} {{}}`"
            subcmds = [(c.name, c.help) for c in cmd.commands.values()]
            subcmds = sorted(subcmds, key=lambda x: x[0])
            subcmds = [
                (template.format(name), help_.split("\n")[0]) for name, help_ in subcmds
            ]
            yield from ["", ".. rubric:: Subcommands", ""]
            yield from rst_list_table(subcmds)

        yield ""

    def create_linkcode(self, ctx, object_name, object_id):
        """Create an external link for the command's documented signature.

        Parameters
        ----------
        ctx : click.Context
            Context with the command.
        object_name : str
            Displace name of the command's documentation object.
        object_id : str
            Internal identifier for the command's documentation object.

        Returns
        -------
        only_node : sphinx.addnodes.only
            The created node that conditionally includes an external link when rendering
            HTML output.
        """
        if not self.resolve_target:
            return None
        info = {
            "module": ctx.command.callback.__module__,
            "fullname": ctx.command.callback.__name__,
        }
        url = self.resolve_target("std", info)
        if not url:
            return None
        only_node = addnodes.only(expr="html")
        only_node += nodes.reference("", "", internal=False, refuri=url)
        only_node[0] += nodes.inline("", "[source]", classes=["viewcode-link"])
        return only_node

    def create_signature(self, ctx, object_name, object_id):
        """Create a signature for the command's documentation object.

        Parameters
        ----------
        ctx : click.Context
            Context with the command.
        object_name : str
            Displace name of the command's documentation object.
        object_id : str
            Internal identifier for the command's documentation object.

        Returns
        -------
        sig_node : sphinx.addnodes.desc_signature
            The created signature node.
        """
        usage = " " + " ".join(ctx.command.collect_usage_pieces(ctx))
        sig_node = addnodes.desc_signature()
        sig_node["names"].append(object_name)
        sig_node["first"] = True
        sig_node["ids"].append(object_id)
        self.state.document.note_explicit_target(sig_node)
        sig_node += addnodes.desc_name(object_name, object_name)
        sig_node += addnodes.desc_addname(usage, usage)
        if "linkcode" in self.options:
            link_node = self.create_linkcode(ctx, object_name, object_id)
            if link_node:
                sig_node += link_node
        return sig_node

    def create_index(self, ctx, object_name, object_id):
        """Create an index for the command's documentation object.

        Parameters
        ----------
        ctx : click.Context
            Context with the command.
        object_name : str
            Displace name of the command's documentation object.
        object_id : str
            Internal identifier for the command's documentation object.

        Returns
        -------
        index_node : sphinx.addnodes.index
            The created index node.
        """
        index_node = addnodes.index(entries=[])
        index_node["entries"].append(
            ("single", f"command; {object_name}", object_id, "", None)
        )
        # Add object to environment
        self.env.domaindata[self.domain]["objects"][self.object_type, object_name] = (
            self.env.docname,
            object_id,
        )
        return index_node

    def create_content(self, ctx, object_name, object_id):
        """Create content for the command's documentation object.

        Parameters
        ----------
        ctx : click.Context
            Context with the command.
        object_name : str
            Displace name of the command's documentation object.
        object_id : str
            Internal identifier for the command's documentation object.

        Returns
        -------
        content_node : sphinx.addnodes.desc_content
            A node containing the command's help text and the documentation for its
            options and subcommands (if present).
        """
        content = StringList()
        for line in self.format_help(ctx):
            content.append(line, self.location)
        content_node = addnodes.desc_content()
        self.state.nested_parse(content, self.content_offset, content_node)
        return content_node

    def document_command(self, ctx):
        """Create node structure documenting a click.Command.

        Parameters
        ----------
        ctx : click.Context
            A context for the command.

        Returns
        -------
        desc_node : sphinx.addnodes.desc
            Root node of the node-tree that describes the command. The node contains
            a ``desc_signature``, a ``desc_content`` and an ``index`` node.
        """
        object_name = nodes.fully_normalize_name(ctx.command_path)
        object_id = nodes.make_id(f"{self.object_type}-{object_name}")

        # Create root node
        desc_node = addnodes.desc()
        desc_node.document = self.state.document
        desc_node["domain"] = self.domain
        desc_node["objtype"] = desc_node["desctype"] = self.object_type
        desc_node["objname"] = object_name

        desc_node += self.create_signature(ctx, object_name, object_id)
        desc_node += self.create_index(ctx, object_name, object_id)
        desc_node += self.create_content(ctx, object_name, object_id)

        return desc_node

    def run(self):
        """Main entry function, called by docutils upon encountering the directive.

        Returns
        -------
        nodes : list[sphinx.addnodes.desc]
            A list of nodes each documenting a command (see :meth:`~.document_command`).
        """
        if ":" in self.name:
            self.domain, self.object_type = self.name.split(":", 1)
        else:
            self.domain, self.object_type = "", self.object_type

        reporter = self.state.document.reporter
        try:
            self.location = reporter.get_source_and_line(self.lineno)
        except AttributeError:
            logger.warning(
                f"Can't determine source for click-cmd directive '{self.arguments[0]}'"
            )

        if "linkcode" in self.options:
            self.resolve_target = getattr(self.env.config, "linkcode_resolve", None)
            if not callable(self.env.config.linkcode_resolve):
                logger.warning(
                    "Function `linkcode_resolve` is not given in conf.py",
                    location=self.location,
                )

        try:
            root_cmd = self.import_command(self.arguments[0])
        except (ImportError, AttributeError, ValueError) as e:
            logger.error(f"Couldn't import click command: {e}", location=self.location)
            return []

        if "name" in self.options:
            root_cmd.name = self.options["name"]
        if "prefix" in self.options:
            root_cmd.name = self.options["prefix"] + " " + root_cmd.name
        max_depth = self.options.get("maxdepth", inf)

        def walk_interface(cmd, parent_ctx, depth):
            """Yield context for command and each of its subcommands."""
            ctx = click.Context(cmd, parent=parent_ctx, info_name=cmd.name)
            yield ctx
            if depth < max_depth:
                try:
                    subcommands = sorted(cmd.commands.values(), key=lambda x: x.name)
                    for subcmd in subcommands:
                        yield from walk_interface(subcmd, ctx, depth + 1)
                except AttributeError:
                    pass

        contexts = list(walk_interface(root_cmd, None, 0))
        nodes = [self.document_command(ctx) for ctx in contexts]

        return nodes


def setup(app):
    """Register extension to sphinx.

    This function registers a directive and role with the name "click-cmd" to
    sphinx's "std" domain. Furthermore it adds itself as a new object type to the
    same domain.

    Parameters
    ----------
    app : sphinx.application.Sphinx
        Main application class and extensibility interface of sphinx.
    """
    app.add_config_value("sphinx_click_cmd_resolve", None, "")
    app.add_directive_to_domain("std", "click-cmd", ClickCmdDirective)
    app.add_role_to_domain("std", "click-cmd", XRefRole())
    # Add as new object type to standard domain
    object_types = app.registry.domain_object_types.setdefault("std", {})
    object_types["click-cmd"] = ObjType("console command", "click-cmd")
