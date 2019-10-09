import tkinter as tk


class CanvasObject:
    def __init__(self, project):
        self.project = project
        self.root = tk.Tk()
        self.width = 480
        self.height = 360
        self.origin = (int(self.width/2), int(self.height/2))
        self.root.title("Scratch To Python by @dantechguy")
        self.root.resizable(False, False)
        self.root.protocol("WM_DELETE_WINDOW", self.project.stop)
        # init
        self.frame_rate = 2
        self.root.iconbitmap("{0}/../favicon.ico".format(__file__))
        self.canvas = tk.Canvas(self.root, width=self.width, height=self.height, bg="#fff", highlightthickness=0)
        self.canvas.pack()

    def run(self):
        self.root.mainloop()