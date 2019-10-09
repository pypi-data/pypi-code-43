


class Sensing:
    def __init__(self, project):
        self._project = project
        self._events = self._project.events
        self._root = self._project.canvas_object.root
        # public with getters
        self._mouse_x = 0
        self._mouse_y = 0
        self._mouse_down = False
        all_keys = list('abcdefghijklmnopqrstuvwxyz0123456789')
        special_keys = 'up down left right space'.split(' ')
        all_keys.extend(special_keys)
        self._keys_down = dict.fromkeys(all_keys, False)

        self._create_bindings()

    # getters

    def mouse_x(self):
        return self._mouse_x

    def mouse_y(self):
        return self._mouse_y

    def mouse_down(self):
        return self._mouse_down

    def key_pressed(self, key):
        return self._keys_down[key]

    # bindings

    def _create_bindings(self):
        self._root.bind('<Motion>', self._mouse_motion)

        self._root.bind('<ButtonPress-1>', self._button_pressed)

        self._root.bind('<ButtonRelease-1>', self._button_released)

        self._root.bind('<KeyPress>', self._key_pressed)

        self._root.bind('<KeyRelease>', self._key_released)

    def _mouse_motion(self, event):
        self._mouse_x = event.x - 240
        self._mouse_y = 180 - event.y

    def _button_pressed(self, event):
        self._mouse_down = True

    def _button_released(self, event):
        self._mouse_down = False

    def _key_pressed(self, event):
        key = event.keysym.lower()
        self._set_key_state(key, True)
        self._events.send_key_pressed_event(key)

    def _key_released(self, event):
        key = event.keysym.lower()
        self._set_key_state(key, False)

    def _set_key_state(self, key, state):
        if key in self._keys_down:
            self._keys_down[key] = state
