from . import canvas_object
from . import sensing
from . import events
from . import scratch_time
import queue
import time
import random



class Project:
    def __init__(self, fps=30):
        self.canvas_object = canvas_object.CanvasObject(self)
        self._queue = queue.Queue()
        self._fps = fps
        self._frame_time_ms = int(1000/fps)
        self._frame_time = 1/fps
        self._last_after_id = None
        # public variables
        self.events = events.Events()
        self.sensing = sensing.Sensing(self)
        self.time = scratch_time.Time()
        self._username = 'username';

    def run(self):
        self.canvas_object.root.after(self._frame_time_ms, self.frame)
        self.time.reset_timer()
        self.events.send_green_flag_event()
        self.canvas_object.root.mainloop()

    def stop(self):
        self.canvas_object.root.after_cancel(self._last_after_id)
        self.canvas_object.root.destroy()

    def frame(self):
        for _ in range(self._queue.qsize()):
            item = self._queue.get()
            item_function = item['function']
            item_parameters = item['parameters']
            item_function(*item_parameters)
            self._queue.task_done()

        self._last_after_id = self.canvas_object.root.after(self._frame_time_ms, self.frame)


    # PUBLIC METHOD
    def add_instruction_to_queue(self, item):
        self._queue.put(item)

    # BLOCKS

    def wait(self, seconds=False):
        if not seconds:
            seconds = self._frame_time
        end = time.time() + seconds
        while time.time() < end:
            self.canvas_object.root.update()

    def switch_backdrop_to(self, parameters): # backdrop name / number
        pass

    def next_backdrop(self, parameters):
        pass

    def stop_all_sounds(self, parameters):
        pass

    def create_clone_of(self, parameters): #sprite
        pass

    def username(self):
        return self._username