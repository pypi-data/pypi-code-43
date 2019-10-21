from pacurses.pulse_audio.output import Output

ABBREVIATION_SUFFIX_STRING = "..."
DEFAULT_PREFIX_STRING = "*"


def abbreviate_text(text, length, stretch=False):
    if len(text) <= length:
        if stretch:
            text += " " * (length - len(text))

        return text

    else:
        relative_length = length - len(ABBREVIATION_SUFFIX_STRING)
        return text[:relative_length] + ABBREVIATION_SUFFIX_STRING


def abbreviate_two_text(text_one, text_two, total_length):
    length_each_text = int(total_length / 2)
    text_one_length = len(text_one)
    text_two_length = len(text_two)

    if text_one_length < length_each_text:
        return (
            text_one,
            abbreviate_text(text_two, total_length - text_one_length),
        )

    if text_two_length < length_each_text:
        return (
            abbreviate_text(text_one, total_length - text_two_length),
            text_two,
        )

    return (
        abbreviate_text(text_one, length_each_text),
        abbreviate_text(text_two, length_each_text),
    )


def abbreviate_sink(sink, sink_type, length, with_state=False, stretch=False):
    default_prefix = (
        DEFAULT_PREFIX_STRING if type(sink) == Output and sink.default else " "
    )
    name = "{0}{1} {2}".format(sink.index, default_prefix, sink.name)
    length = length - len(default_prefix) - 3
    if not with_state:
        return abbreviate_text(name, length, stretch=stretch)

    else:
        state = "{0}%{1}".format(sink.volume, " (muted)" if sink.muted else "")
        name, state = abbreviate_two_text(name, state, length)
        return "{0} - {1}".format(name, state)
