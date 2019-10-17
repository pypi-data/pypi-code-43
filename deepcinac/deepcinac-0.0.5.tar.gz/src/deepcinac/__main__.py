import sys
if sys.version_info[0] < 3:
    from Tkinter import *
else:
    from tkinter import *

from deepcinac.gui.cinac_gui import ChoiceFormatFrame

root = Tk()
root.title(f"Options")

app = ChoiceFormatFrame(master=root, default_path=None)
app.mainloop()
