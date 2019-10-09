import inspect

colref = "(string: name of column in `data_frame`)"
colref_list = "(list of string: names of columns in `data_frame`)"

docs = dict(
    data_frame=["A 'tidy' `pandas.DataFrame`"],
    color_discrete_sequence=[
        "(list of valid CSS-color strings)",
        "When `color` is set and the values in the corresponding column are not numeric, values in that column are assigned colors by cycling through `color_discrete_sequence` in the order described in `category_orders`, unless the value of `color` is a key in `color_discrete_map`.",
        "Various useful color sequences are available in the `dataverk_tools.colors` submodules, specifically `dataverk_tools.colors.qualitative`.",
    ],
    color_discrete_map=[
        "(dict with string keys and values that are valid CSS-color strings, default `{}`)",
        "Used to override `color_discrete_sequence` to assign a specific colors to marks corresponding with specific values.",
        "Keys in `color_discrete_map` should be values in the column denoted by `color`.",
    ],
    color_continuous_scale=[
        "(list of valid CSS-color strings)",
        "This list is used to build a continuous color scale when the column denoted by `color` contains numeric data.",
        "Various useful color scales are available in the `dataverk_tools.colors` submodules, specifically `dataverk_tools.colors.sequential`, `dataverk_tools.colors.diverging` and `dataverk_tools.colors.cyclical`.",
    ]
)


def make_docstring(fn):
    result = (fn.__doc__ or "") + "\nArguments:\n"
    for arg in inspect.getargspec(fn)[0]:
        d = (
            " ".join(docs[arg] or "")
            if arg in docs
            else "(documentation missing from map)"
        )
        result += "    %s: %s\n" % (arg, d)
    result += "Returns:\n"
    result += "    A `dataverk_tools` object."
    return result
