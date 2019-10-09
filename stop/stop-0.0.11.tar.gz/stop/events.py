import threading

class Events:
    def __init__(self):
        self.green_flag_events = {'all':[]}
        self.key_pressed_events = {}
        self.sprite_clicked_events = {}
        self.backdrop_switches_to_events = {}
        self.loudness_more_than_events = {}
        self.timer_more_than_events = {}
        self.receive_broadcast_events = {}

    # ADD EVENTS

    def add_green_flag_event(self, function):
        self._add_event('all', function, self.green_flag_events)

    def add_key_pressed_event(self, key, function):
        self._add_event(key, function, self.key_pressed_events)

    def add_sprite_clicked_event(self, sprite, function):
        self._add_event(sprite, function, self.sprite_clicked_events)

    def add_backdrop_switches_to_event(self, backdrop_name, function):
        pass

    def add_loudness_more_than_event(self, loudness, function):
        pass

    def add_timer_more_than_event(self, timer, function):
        pass

    def add_receive_broadcast_event(self, message, function):
        self._add_event(message, function, self.receive_broadcast_events)

    def _add_event(self, key, function, events_list):
        if key not in events_list:
            events_list[key] = []
        events_list[key].append(function)

    # SEND EVENTS

    def send_green_flag_event(self):
        self._send_event('all', self.green_flag_events)

    def send_key_pressed_event(self, key):
        self._send_event(key, self.key_pressed_events)

    def send_sprite_clicked_event(self, sprite):
        self._send_event(sprite, self.sprite_clicked_events)

    def send_backdrop_switches_to_event(self, backdrop_name):
        self._send_event(backdrop_name, self.backdrop_switches_to_events)

    def send_loudness_more_than_event(self, loudness):
        self._send_event(loudness, self.loudness_more_than_events)

    def send_timer_more_than_event(self, timer):
        self._send_event(timer, self.timer_more_than_events)

    def send_receive_broadcast_event(self, message):
        self._send_event(message, self.receive_broadcast_events)

    def send_receive_broadcast_event_and_wait(self, message):
        pass

    def _send_event(self, key, events_list):
        if key in events_list:
            specific_events_list = events_list[key]

            threads = []
            for method in specific_events_list:
                temp_thread = threading.Thread(target=method, daemon=True)
                threads.append(temp_thread)

            for thread in threads:
                thread.start()