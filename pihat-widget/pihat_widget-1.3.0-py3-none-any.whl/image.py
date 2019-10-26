from tkinter import *
import time
import os
import multiprocessing as mp

path = os.path.abspath(__file__)
dir_path = os.path.dirname(path)

images_path = os.path.join(dir_path,"images\\")
class ImageLoader:

    def __del__(self):
        self.__continue_proc = False
        self.__q.close()


    @property
    def q(self):
        return self.__q

    def __init__(self,origin_x=5, origin_y=5, origin_width=140, origin_height=330, offsetx=10,offsety=10):

        self.__origin_x = origin_x
        self.__origin_y = origin_y
        self.__origin_width = origin_width
        self.__origin_height = origin_height
        self.__offset_x=offsetx
        self.__offset_y = offsety
        self.__continue_proc = True
        self.__q = mp.Queue()
        self.__p = None
        self.__root = None
        self.__canvas = None
        self.__show()

    def close(self):
        self.q.put(("close",""))
    def _display_image(self, q):
        self.__root = Tk()
        self.__root.geometry('+%d+%d' % (self.__origin_x, self.__origin_y))
        self.__root.overrideredirect(True)

        def __on_closing():
            self.__continue_proc=False


        self.__root.protocol("WM_DELETE_WINDOW", __on_closing)

        self.__canvas = Canvas(self.__root, width=self.__origin_width, height=self.__origin_height)
        self.__canvas.pack()

        while self.__continue_proc:
            self.__root.update_idletasks()
            if q.qsize()>0:
                action, result = q.get(block=True)
                if action=="load":
                    img = PhotoImage(file=f"{images_path}{result}.png")

                    self.__canvas.create_image(self.__offset_x, self.__offset_y, anchor=NW, image=img)
                elif action=="close":
                    self.__continue_proc = False

                    self.q.close()
                    self.__root.destroy()
                    break
                #img.subsample(self.__zoom_x, self.__zoom_y)
            self.__root.update()


    def __show (self):

        self.__p=mp.Process(target=self._display_image, args=(self.__q,))

        self.__p.start()
        #p.join()


