import importlib
import inspect
import logging
import re

log = logging.getLogger("pymdgen")


def adjust_header_indent(line, section_level):
    """
    Parses a line for a markdown header and fixes the
    indent for the specified section level

    eg. '## Header' with section_level=1 will become
    '# Header"

    Arguments:

    - line(str)
    - section_level(int)

    Returns:

    - str
    """

    m = re.match("[#+] (.+)", line)
    if m:
        line = u"{} {}".format("#" * (section_level), m.group(1))
    return line


def getargspec(func):
    """
    Wrapper for inspect.getargspec that supports
    decorated functions
    """
    if hasattr(func, "__wrapped__"):
        return inspect.getargspec(func.__wrapped__)
    return inspect.getargspec(func)


def doc_func(name, func, section_level=4):

    """
    return markdown formatted documentation for a function

    Arguments:

    - name(str): function name #FIXME: why is this manual?
    - func(function)
    - section_level(int): markdown section level
    """

    is_property = False

    if isinstance(func, property):
        func = func.fget
        is_property = True

    output = []
    docstr = inspect.getdoc(func)
    # skip functions without a docstr
    if not docstr:
        return output

    spec = getargspec(func)
    display = []
    end_args = []

    # *args and **kwargs
    if spec[1]:
        end_args.append("*" + spec[1])
    if spec[2]:
        end_args.append("**" + spec[2])

    # check for args with defaults
    if spec[3]:
        args = spec[0][-len(spec[3]) :]
        default_args = list(zip(args, spec[3]))

        # set args to rest
        args = spec[0][: -len(spec[3])]
    else:
        args = spec[0]
        default_args = []

    if args:
        display.append(", ".join(args))
    if default_args:
        display.append(", ".join("%s=%s" % x for x in default_args))
    if end_args:
        display.append(", ".join(end_args))

    if name.find("__") == 0:
        title = "\{}".format(name)
    else:
        title = name
    param_str = "(" + ", ".join(display) + ")"

    output.append("{} {}".format("#" * section_level, title))
    output.append("`def {}{}`".format(name, param_str))
    output.append("")
    output.append(docstr)
    output.append("")
    output.append("---")

    return output


def parse_class_docstr(docstr, list_class_attributes, section_level):

    """
    Takes a class doc string markdown and parses it line for line
    to fix and header indent issues as well as collect instanced
    attribute docs

    Arguments

    - docstr(str): markdown formatted class docstr
    - list_class_attributes(list): collect instance attribute docs into
      this list
    - section_level(int): header indent level

    Returns:

    - list: parsed/fixed output split into lines
    """

    attributes_regex = "[#+] Instanced (Attributes|Properties)"
    header_regex = "[#+] (.+)"

    collect_attributes = False
    out = []

    for line in docstr.split("\n"):
        if re.match(attributes_regex, line):
            collect_attributes = True
        elif collect_attributes and line.strip():
            list_class_attributes.append(line)
        elif collect_attributes and list_class_attributes and not line.strip():
            collect_attributes = False
        else:
            out.append(adjust_header_indent(line, section_level + 1))

    return out


def doc_class(name, cls, section_level=3):
    """
    return markdown formatted documentation for a class

    Arguments

    - name(str): function name #FIXME: why is this manual?
    - cls(class)
    - section_level(int): markdown section level
    """

    output = []
    docstr = inspect.getdoc(cls)
    # skip functions without a docstr
    if not docstr:
        return output

    head_indent = "#" * (section_level + 1)

    out_class_attributes = ["", "{} Class Attributes".format(head_indent), ""]
    out_instanced_attributes = [
        "",
        "{} Instanced Attributes".format(head_indent),
        "",
        "These attributes / properties will be available on instances of the class",
        "",
    ]

    out_class_methods = ["", "{} Class Methods".format(head_indent), ""]
    out_methods = ["", "{} Methods".format(head_indent), ""]

    list_instanced_attributes = []
    list_class_attributes = []
    list_class_methods = []
    list_methods = []

    # parse the class docstr markdown to:
    # - fix header indent according to section level
    # - collect arbitrary instance attribute documentation
    out_docstr = parse_class_docstr(docstr, list_instanced_attributes, section_level)

    # full mro is probably overkill?
    # base_classes = inspect.getmro(cls)
    base_classes = cls.__bases__
    base_classes = (c.__module__ + "." + c.__name__ for c in base_classes)

    output.append("{} {}".format("#" * section_level, name))
    output.append("")
    output.append("```")
    output.append(name + "(" + ", ".join(base_classes) + ")")
    output.append("```")
    output.append("")
    output.extend(out_docstr)
    output.append("")

    functions = sorted(list(cls.__dict__.items()), key=lambda x: x[0])

    for func_name, func in functions:
        if inspect.isfunction(func):
            list_methods.extend(doc_func(func_name, func, section_level + 2))
        elif isinstance(func, classmethod):
            list_class_methods.extend(
                doc_func(func_name, func.__func__, section_level + 2)
            )
        elif isinstance(func, property):
            list_instanced_attributes.extend(doc_property(func_name, func))
        elif hasattr(func, "help"):
            list_class_attributes.extend(doc_attribute(func_name, func))

    # Append class attribute documentation to output

    if list_class_attributes:
        output.extend(out_class_attributes)
        output.extend(sorted(list_class_attributes))

    # Append instanced attributed documentation to output

    if list_instanced_attributes:
        output.extend(out_instanced_attributes)
        output.extend(sorted(list_instanced_attributes))

    # Appemd class method documentation to output

    if list_class_methods:
        output.extend(out_class_methods)
        output.extend(list_class_methods)

    # Append method documentation to output

    if list_methods:
        output.extend(out_methods)
        output.extend(list_methods)

    output.append("")

    return output


def doc_attribute(name, attribute):
    """
    return markdown formatted documentation for a class attribute

    This is an experimental feature that will document any attribute
    set on class as long as the attribute it self has `help` property

    Argument(s):

    - name(str)
    - attribute(function|class|instance)

    Returns:

    - list
    """
    if not hasattr(attribute, "help"):
        return

    output = []
    type_name = None

    if hasattr(attribute, "pymdgen_type_info"):
        type_name = "`{}`".format(attribute.pymdgen_type_info)
    elif inspect.isclass(attribute):
        type_name = "`{} Class`".format(attribute.__name__)
    elif hasattr(attribute, "__class__"):
        type_name = "`{} Instance`".format(attribute.__class__.__name__)

    try:
        output.append("- {} ({}): {}".format(name, type_name, attribute.help))
    except:
        pass

    return output


def doc_property(name, prop):
    """
    return markdown formatted documentation for a class property

    Argument(s):

    - name(str)
    - prop(property)

    Returns:

    - list
    """
    docstr = inspect.getdoc(prop.fget)
    return ["- {} (`{}`): {}".format(name, "@property", docstr)]


def doc_module(name, debug=False, section_level=3):

    """
    return markdown formatted documentation for a module

    Arguments:

    - name(str): module name
    - debug(bool): log debug messages
    - section_level(int): markdown section level
    """

    if "/" in name or name.endswith(".py"):
        name = name.replace("/", ".")
        name = name.rstrip(".py")

    module = importlib.import_module(name)
    output = []

    head_indent = "#" * (section_level)

    output.append("{} {}".format(head_indent, module.__name__))

    out_classes = ["{} Classes".format(head_indent), "---", ""]
    out_functions = ["{} Functions".format(head_indent), "---", ""]

    docstr = inspect.getdoc(module)
    if docstr:
        output.extend(["", docstr])

    output.append("")

    for k, v in inspect.getmembers(module):
        if k == "__builtins__":
            continue
        log.debug("checking %s:%s" % (v, k))
        if inspect.isfunction(v):
            if v.__module__ == module.__name__:
                out_functions.extend(doc_func(k, v, section_level + 1))
        if inspect.isclass(v):
            if v.__module__ == module.__name__:
                out_classes.extend(doc_class(k, v, section_level + 1))

    if len(out_functions) > 3:
        output.extend(out_functions)

    if len(out_classes) > 3:
        output.extend(out_classes)

    return output
