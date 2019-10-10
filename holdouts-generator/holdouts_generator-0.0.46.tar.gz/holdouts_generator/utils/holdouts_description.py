def get_level_description(level: int)->str:
    """Return description for given holdouts level.
        level:int, an integer represeting the holdouts level.
    """
    if level == 0:
        return "Holdouts"
    if level == 1:
        return "Inner holdouts"
    return "Inner holdouts (level {level})".format(level=level)