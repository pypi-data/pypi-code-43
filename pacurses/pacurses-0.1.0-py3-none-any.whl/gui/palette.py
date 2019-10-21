from pacurses.constants.palette_names import PaletteNames

palette = [
    (PaletteNames.HEADER, "bold,standout", ""),
    (PaletteNames.UNDERLINE, "underline", ""),
    (PaletteNames.REVERSED, "standout", ""),
    (PaletteNames.WARNING, "light red", ""),
    (PaletteNames.PROGRESS_BAR_NORMAL_FOCUSED, "", ""),
    (PaletteNames.PROGRESS_BAR_COMPLETE_FOCUSED, "standout", ""),
    (PaletteNames.PROGRESS_BAR_NORMAL, "", ""),
    (PaletteNames.PROGRESS_BAR_COMPLETE, "white", "black"),
]
