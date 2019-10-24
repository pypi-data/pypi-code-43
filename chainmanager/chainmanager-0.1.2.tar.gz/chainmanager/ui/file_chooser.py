import sys
import eel
try:
    from tkinter import Tk
except ImportError:
    print("Error: tkinter not found")
    print('For linux, you can install tkinter by executing: "sudo apt-get install python3-tk"')
    sys.exit(1)


from jinja2.exceptions import SecurityError
from pathlib import Path
from tkinter.filedialog import askopenfilename, TclError


class FileChooser:
    def __init__(self):
        self.root = Tk()

    def open_dialog(self, file_type, original_path=""):
        # Esto es para qu eno salgan los ocultos
        try:
            # call a dummy dialog with an impossible option to initialize the file
            # dialog without really getting a dialog window; this will throw a
            # TclError, so we need a try...except :
            self.root.tk.call('tk_getOpenFile', '-foobarbaz')
            # now set the magic variables accordingly
            self.root.tk.call('set', '::tk::dialog::file::showHiddenBtn', '1')
            self.root.tk.call('set', '::tk::dialog::file::showHiddenVar', '0')
        except TclError:
            eel.show_warning(
                'tkinter library is not available for your OS. Please paste the path to your xlsx file on the box.')
            return original_path

        self.root.withdraw()
        self.root.wm_attributes('-topmost', 1)

        self.root.tk.call('set', '::tk::dialog::file::showHiddenVar', '0')
        if file_type == 'excel':
            file_types = [('Excel files', '*.xlsx'), ('All files', '*')]
        else:
            file_types = [('All files', '*')]
        file_path = askopenfilename(initialdir=str(Path.home()), parent=self.root, filetypes=file_types)
        self.root.update()

        return file_path
