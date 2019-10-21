# coding=utf-8

import re
from collections import defaultdict
from xml.etree import ElementTree as ET

# ------------------------------------------------------------------------------

# Basic configuration - modify this to change output formatting
_block_configuration = {
    "chapter": {
        "markdown_heading": "##",
        "pretty_name": "",
        "show_count": False
    },
    "enumerate": {
        "line_indent_char": "",
        "list_heading": "1. ",
        "markdown_heading": "",
        "pretty_name": "",
        "show_count": False
    },
    "exer": {
        "line_indent_char": "> ",
        "markdown_heading": "####",
        "pretty_name": "Exercise",
        "show_count": True
    },
    "itemize": {
        "line_indent_char": "",
        "list_heading": "* ",
        "markdown_heading": "",
        "pretty_name": "",
        "show_count": False
    },
    "lem": {
        "line_indent_char": "> ",
        "markdown_heading": "####",
        "pretty_name": "Lemma",
        "show_count": True
    },
    "lstlisting": {
        "line_indent_char": "    ",
        "markdown_heading": "",
        "pretty_name": "",
        "show_count": False
    },
    "proof": {
        "line_indent_char": "",
        "markdown_heading": "####",
        "pretty_name": "Proof",
        "show_count": False
    },
    "prop": {
        "line_indent_char": "> ",
        "markdown_heading": "####",
        "pretty_name": "Proposition",
        "show_count": True
    },
    "section": {
        "markdown_heading": "###",
        "pretty_name": "",
        "show_count": False
    },
    "subsection": {
        "markdown_heading": "####",
        "pretty_name": "",
        "show_count": False
    },
    "thm": {
        "line_indent_char": "> ",
        "markdown_heading": "####",
        "pretty_name": "Theorem",
        "show_count": True
    }
}


# ------------------------------------------------------------------------------

class LaTeX2Markdown(object):
    """Initialise with a LaTeX string - see the main routine for examples of
    reading this string from an existing .tex file.

    To modify the outputted markdown, modify the _block_configuration variable
    before initializing the LaTeX2Markdown instance."""

    def __init__(self, config_path, latex_string,
                 block_configuration=_block_configuration,
                 block_counter=defaultdict(lambda: 1)):

        self._block_configuration = block_configuration
        self._latex_string = latex_string
        self._block_counter = block_counter
        self._config_xml_root = ET.parse(config_path).getroot()

        # Precompile the regexes

        # Select everything in the main matter
        self._main_re = re.compile(r"""\\begin{document}
                                    (?P<main>.*)
                                    \\end{document}""",
                                   flags=re.DOTALL + re.VERBOSE)

        # Select all our block materials.
        self._block_re = re.compile(r"""\\begin{(?P<block_name>exer|proof|thm|lem|prop)} # block name
                                    (\[(?P<block_title>.*?)\])? # Optional block title
                                    (?P<block_contents>.*?) # Non-greedy block contents
                                    \\end{(?P=block_name)}""",  # closing block
                                    flags=re.DOTALL + re.VERBOSE)

        # Select all our list blocks
        self._lists_re = re.compile(r"""\\begin{(?P<block_name>enumerate|itemize)} # list name
                                    (\[.*?\])? # Optional enumerate settings i.e. (a)
                                    (?P<block_contents>.*?) # Non-greedy list contents
                                    \\end{(?P=block_name)}""",  # closing list
                                    flags=re.DOTALL + re.VERBOSE)

        # Select all our headers
        self._header_re = re.compile(r"""\\(?P<header_name>chapter|section|subsection) # Header
                                    {(?P<header_contents>.*?)}""",  # Header title
                                     flags=re.DOTALL + re.VERBOSE)

        # Select all our 'auxillary blocks' - these need special treatment
        # for future use - e.g. pygments highlighting instead of code blocks
        # in Markdown
        self._aux_block_re = re.compile(r"""\\begin{(?P<block_name>lstlisting)} # block name
                                    (?P<block_contents>.*?) # Non-greedy block contents
                                    \\end{(?P=block_name)}""",  # closing block
                                        flags=re.DOTALL + re.VERBOSE)

    def _replace_header(self, matchobj):
        """Creates a header string for a section/subsection/chapter match.
        For example, "### 2 - Integral Calculus\n" """

        header_name = matchobj.group('header_name')
        header_contents = matchobj.group('header_contents')

        header = self._format_block_name(header_name)

        block_config = self._block_configuration[header_name]

        # If we have a count, separate the title from the count with a dash
        separator = "-" if block_config.get("show_count") else ""

        output_str = "{header} {separator} {title}\n".format(
            header=header,
            title=header_contents,
            separator=separator)

        return output_str

    def _replace_block(self, matchobj):
        """Create a string that replaces an entire block.
        The string consists of a header (e.g. ### Exercise 1)
        and a block, containing the LaTeX code.

        The block may be optionally indented, blockquoted, etc.
        These settings are customizable through the config.json
        file"""

        block_name = matchobj.group('block_name')
        block_contents = matchobj.group('block_contents')
        # Block title may not exist, so use .get method
        block_title = matchobj.groupdict().get('block_title')

        # We have to format differently for lists
        if block_name in {"itemize", "enumerate"}:
            formatted_contents = self._format_list_contents(block_name,
                                                            block_contents)
        else:
            formatted_contents = self._format_block_contents(block_name,
                                                             block_contents)

        header = self._format_block_name(block_name, block_title)

        output_str = "{header}\n\n{block_contents}".format(
            header=header,
            block_contents=formatted_contents)
        return output_str

    def _format_block_contents(self, block_name, block_contents):
        """Format the contents of a block with configuration parameters
        provided in the self._block_configuration attribute"""

        block_config = self._block_configuration[block_name]

        line_indent_char = block_config["line_indent_char"]

        output_str = ""
        for line in block_contents.lstrip().rstrip().split("\n"):
            line = line.lstrip().rstrip()
            indented_line = line_indent_char + line + "\n"
            output_str += indented_line
        return output_str

    def _format_list_contents(self, block_name, block_contents):
        """To format a list, we must remove the \item declaration in the
        LaTeX source.  All else is as in the _format_block_contents method."""
        block_config = self._block_configuration[block_name]

        list_heading = block_config["list_heading"]

        output_str = ""
        for line in block_contents.lstrip().rstrip().split("\n"):
            line = line.lstrip().rstrip()
            markdown_list_line = line.replace(r"\item", list_heading)
            output_str += markdown_list_line + "\n"
        return output_str

    def _format_block_name(self, block_name, block_title=None):
        """Format the Markdown header associated with a block.
        Due to the optional block_title, we split the string construction
        into two parts."""

        block_config = self._block_configuration[block_name]
        pretty_name = block_config["pretty_name"]
        show_count = block_config["show_count"]
        markdown_heading = block_config["markdown_heading"]

        block_count = self._block_counter[block_name] if show_count else ""
        self._block_counter[block_name] += 1

        output_str = "{markdown_heading} {pretty_name} {block_count}".format(
            markdown_heading=markdown_heading,
            pretty_name=pretty_name,
            block_count=block_count)

        if block_title:
            output_str = "{output_str} ({block_title})".format(
                output_str=output_str,
                block_title=block_title)

        return output_str.lstrip().rstrip()

    def _latex_to_markdown(self):
        """Main function, returns the formatted Markdown as a string.
        Uses a lot of custom regexes to fix a lot of content - you may have
        to add or remove some regexes to suit your own needs."""

        # Get main content, skipping preamble and closing tags.
        try:
            output = self._main_re.search(self._latex_string).group("main")
        except AttributeError:
            output = self._latex_string

        # Reformat, lists, blocks, and headers.
        output = self._lists_re.sub(self._replace_block, output)
        output = self._block_re.sub(self._replace_block, output)
        output = self._header_re.sub(self._replace_header, output)
        output = self._aux_block_re.sub(self._replace_block, output)

        # Fix \\ formatting for line breaks in align blocks
        output = re.sub(r" \\\\", r" \\\\\\\\", output)
        # Convert align* block  to align - this fixes formatting
        output = re.sub(r"align\*", r"align", output)

        # Fix emph, textbf, texttt formatting
        output = re.sub(r"~", self.convert_lable_to_character_entity, output)
        output = re.sub(r"\\includegraphics\[[^\[^\]^\{^\}]+\]\{[^\{^\}]+\}", self.replace_LaTex_img_url, output)
        output = re.sub(r"\\[u]ppi", r"\pi", output)
        output = re.sub(r"\\Up[pP]i", r"\Pi", output)
        output = re.sub(r"\\[Uu]Ppi", r"\Pi", output)
        output = re.sub(r"\\[Uu]palpha", r"\alpha", output)
        output = re.sub(r"\\[Uu]pAlpha", r"\Alpha", output)
        output = re.sub(r"\\[u]pdelta", r"\delta", output)
        output = re.sub(r"\\[Uu]pDelta", r"\Delta", output)
        output = re.sub(r"\\Up[Dd]elta", r"\Delta", output)
        output = re.sub(r"\\[tT]ext[bB]ack[sS]lash", r"\backslash", output)
        output = re.sub(r"{\\textbar}", self.convert_lable_to_character_entity, output)
        output = re.sub(r"{\\textbar}", self.convert_lable_to_character_entity, output)
        output = re.sub(r"{\\ldots}", self.convert_lable_to_character_entity, output)
        output = re.sub(r"{\\textgreater}", self.convert_lable_to_character_entity, output)
        output = re.sub(r"\\textasciicircum{(.*?)}", self.convert_lable_to_character_entity, output)
        output = re.sub(r"\\textasciitilde{(.*?)}", self.convert_lable_to_character_entity, output)
        output = re.sub(r"\\emph{(.*?)}", r"*\1*", output)
        output = re.sub(r"\\textit\{[^{^}]*\}", self.gen_dolor, output)
        output = re.sub(r"\\textbf{(.*?)}", r" **\1** ", output)
        output = re.sub(r"\\raisebox{[-+0-9\\.]*pt}{(.*?)}", r" **\1** ", output)
        output = re.sub(r"\\underline{(.*?)}", self.gen_underline, output)
        output = re.sub(r"\\nsubset ", r"\\not\\subset ", output)
        output = re.sub(r"\\texttt{(.*?)}", self.gen_dolor, output)
        output = re.sub(r"\\textit{(.*?)}", self.gen_dolor, output)
        output = re.sub(r"\\ding\{[0-9]+\}\\ding\{[0-9]+\}", self.convert_lable_to_character_entity, output)
        output = re.sub(r"\\ding{(.*?)}", self.convert_lable_to_character_entity, output)
        # output = re.sub(r"\\includegraphics\[[^\[^\]^\{^\}]+\]\{[^\{^\}]+\}", self.replace_LaTex_img_url, output)
        output = re.sub(r"``[^`^']+''", self.replace_quotation_marks, output)
        output = re.sub(r"@\d{3}[A-Z_]{2,5}\|[A-Z]\d{1,3}(\\#\d{1,3})*@", self.fix_paper_mark, output)
        output = re.sub(r'\\begin\{table\}(?P<content>[\s\S]*?)\\end\{table\}', self.replace_laTex_table, output)
        output = re.sub(r'\\begin{equation[\*]{0,1}}[\n\t\r]{0,1}([\s\S]*?)[\n\t\r]{0,1}\\end{equation[\*]{0,1}}',
                        r'$\1$', output)
        output = re.sub(r'\\begin{align}([\s\S]*?)\\end{align}', r'$\\begin{aligned}\1\\end{aligned}$', output)
        output = re.sub(r'\$\{\\times\}\$', self.convert_lable_to_character_entity, output)
        output = re.sub(r'\$\{\\div\}\$', self.convert_lable_to_character_entity, output)

        output = re.sub(r"\\newline", r"\n", output)
        # Fix \% formatting
        output = re.sub(r"\\%", r"%", output)
        # Fix argmax, etc.
        output = re.sub(r"\\arg(max|min)", r"\\text{arg\1}", output)

        #format formula
        output = re.sub(r"(\\[A-Za-z^\\]+)( \$)", r"\1$", output)
        # Throw away content in IGNORE/END block
        output = re.sub(r"% LaTeX2Markdown IGNORE(.*?)\% LaTeX2Markdown END",
                        "", output, flags=re.DOTALL)
        return output.lstrip().rstrip()

    def to_markdown(self):
        return self._latex_to_markdown()

    def gen_underline(self, matched):
        source = matched.group()
        regex = r"\\underline{(.*?)}"
        new_match = re.match(regex, source)
        w = new_match.group(1)
        z = re.sub(r"\s\s", "　", w)
        z = re.sub(r"\s", "&emsp;", z)
        return "<u>%s</u>" % z


    def gen_dolor(self, matched):
        source = matched.group()
        ret = re.findall(r"(?<=\{)(.+?)(?=\})", source)
        if len(ret) > 0:
            return "$%s$ " % ret[0]
        return source

    def replace_LaTex_img_url(self, matched):
        graphic = matched.group()
        url = re.findall(r"(?<=\{)(.+?)(?=\})", graphic)
        if len(url) > 0:
            return "![](%s)" % url[0]
        return graphic

    def fix_paper_mark(self, matched):
        value = matched.group()
        value = re.sub(r'\\#', r'#', value)
        return value

    def replace_quotation_marks(self, matched):
        value = matched.group()
        value = value.replace("``", "").replace("''", "")
        return '''"%s"''' % value

    def replace_laTex_table(self, matched):
        table = matched.group()
        ret = self.convert_table(table)
        return ret

    def to_latex(self):
        return self._latex_string

    def convert_lable_to_character_entity(self, lable):
        var = lable.group()
        regx = r"./char[@string='%s']" % var
        charNodes = self._config_xml_root.findall(regx)
        if len(charNodes) > 0:
            ret = charNodes[0].attrib['character'].encode("utf-8")
            return ret
        return var

    def convert_table(self, table):
        ret = ''
        is_head = True
        for line in table.split("\n"):
            if '&' in line:
                line = re.sub(r"\\\\+(hline)?$", '', line)
                values = line.replace("&", "|")
                values = "|%s|\n" % values
                ret += values
                if is_head:
                    split_line = re.sub(r'[^\|]', r"-", values)
                    split_line = re.sub(r'(\|-)$', r"|", split_line)
                    ret += split_line + '\n'
                    is_head = False
        return ret


# ------------------------------------------------------------------------------

if __name__ == '__main__':
    import sys
    import os

    # base_path = os.path.dirname(__file__) + "/latex2markdown-bbsmp"
    base_path = os.path.dirname(__file__)
    config_xml = base_path + "/config/charmap.xml"
    printResult = False
    if len(sys.argv) <= 1:
        input_file = base_path + "/config/latex_sample.tex"
        output_file = base_path + "/config/converted_latex_sample.md"
    elif len(sys.argv) == 2:
        input_file, output_file = sys.argv[1], sys.argv[2]
    else:
        input_file, output_file, print_arg = sys.argv[1], sys.argv[2], sys.argv[3]
        if print_arg is not None:
            printResult = True

    with open(input_file, 'r') as f:
        latex_string = f.read()
        y = LaTeX2Markdown(config_xml, latex_string)
        markdown_string = y.to_markdown()
        # if not printResult:
        with open(output_file, 'w') as f_out:
            f_out.write(markdown_string)
        # else:
        #     print(markdown_string)
        print(markdown_string)
