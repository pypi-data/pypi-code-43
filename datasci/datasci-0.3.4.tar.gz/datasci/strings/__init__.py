printable_table = {
    # ord("\a"): "⏰",  # 7 = "BELL" (U+0007) -> "ALARM" (U+23F0)  # [alternative]
    ord("\a"): "🔔",  # 7 = "BELL" (U+0007) -> "BELL" (U+1F514)
    ord("\b"): "🔙",  # 8 = "BACKSPACE" (U+0008) -> "BACK WITH LEFTWARDS ARROW ABOVE" (U+1F519)
    ord("\t"): "⇥",  # 9 = "CHARACTER TABULATION" (U+0009) -> "RIGHTWARDS ARROW TO BAR" (U+21E5)
    ord("\n"): "⏎",  # 10 = "LINE FEED (LF)" (U+000A) -> "RETURN SYMBOL" (U+23CE)
    ord("\v"): "␋",  # 11 = "LINE TABULATION" (U+000B) -> "SYMBOL FOR VERTICAL TABULATION" (U+240B)
    ord("\f"): "␌",  # 12 "FORM FEED (FF)" (U+000C) -> "SYMBOL FOR FORM FEED" (U+240C)
    ord("\r"): "␍",  # 13 "CARRIAGE RETURN (CR)" (U+000D) -> "SYMBOL FOR CARRIAGE RETURN" (U+240D)
    # ord(" "): "•",  # 32 "SPACE" (U+0020) -> "BULLET" (U+2022)  # [alternative]
    ord(" "): "·",  # 32 "SPACE" (U+0020) -> "MIDDLE DOT" (U+00B7)
}
# TODO: anything for ␉ = "SYMBOL FOR HORIZONTAL TABULATION" (U+2409) ?


def printable(value: str) -> str:
    """
    Replace "non-printable" characters in a string with printable alternatives.
    """
    return value.translate(printable_table)

# v- fails because str.translate takes no keyword arguments :(
# printable = partial(str.translate, table=printable_table)

# printable("Hello world!\nRightbackatcha.")
