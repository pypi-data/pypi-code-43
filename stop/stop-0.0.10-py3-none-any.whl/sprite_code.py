import tkinter as tk
from . import scratch_math as v
from . import sprite
import random
from PIL import Image, ImageTk
import os 

class SpriteCode:
    def __init__(self, parameters):
        # private
        self._project =             parameters['project']
        self._canvas =              self._project.canvas_object
        self._sprite_parent =       parameters['sprite_parent']
        self._touching_mouse =      False
        # private builtin
        self._layer_order =         parameters['layer_order']       # number
        self._is_clone =            parameters['is_clone']
        self._visible =             parameters['visible']           # true / false
        self._draggable =           parameters['draggable']         # True / False
        self._rotation_style =      parameters['rotation_style']    # Left-Right / Dont Rotate / All Around
        self._costumes =            parameters['costumes']          # list of dict of name and image dir
        # builtin with public getters
        self._x =                   parameters['x']
        self._y =                   parameters['y']                                 
        self._direction =           parameters['direction']         # angle -179 to 180
        self._size =                parameters['size']              # percentage 0 to 100
        self._costume_number =      parameters['costume_number']    # index starts 0
        self._volume =              parameters['volume']            # percentage 0 to 100
        self._answer =              parameters['answer']
        # NOT BUILT INS
        # creating canvas image
        self._canvas_img = self._canvas.canvas.create_image((0, 0))
        self._pil_img = None
        self._pil_img_edited = None
        self._tk_img = None
        
        self._update_position()
        self._update_sprite()
        self._set_bindings()

    # motion
    def move_steps(self, steps):
        x = 0
        y = 0
        if self._direction == 0:
            y = steps
        elif self._direction == 90:
            x = steps
        elif self._direction == 180:
            y = 0 - steps
        elif self._direction == -90:
            x = 0 - steps
        else:
            x = steps*v.sin(self._direction)
            y = steps*v.cos(self._direction)
        self._x += x
        self._y += y
        self._update_position()

    def turn_right_degrees(self, degrees):
        new_direction = self._direction + degrees
        self.point_in_direction(new_direction)

    def turn_left_degrees(self, degrees):
        new_direction = self._direction - degrees
        self.point_in_direction(new_direction)

    def go_to(self, option):
        if option == "random_position":
            x = random.randint(-240, 240)
            y = random.randint(-180, 180)
        elif option == "mouse_pointer":
            # use system to find mouse coordinates
            x = self._project.sensing.mouse_x()
            y = self._project.sensing.mouse_y()
        else:
            # use system to find other sprite coordinates
            x = option.x()
            y = option.y()
        self._x = x
        self._y = y
        self._update_position()

    def go_to_x_y(self, x, y):
        self._x = x
        self._y = y
        self._update_position()

    def glide_seconds_to(self, option, seconds):
        if option == "random_position":
            x = random.randint(-240, 240)
            y = random.randint(-180, 180)
        elif option == "mouse_pointer":
            # use system to find mouse coordinates
            x = self._project.sensing.mouse_x()
            y = self._project.sensing.mouse_y()
        else:
            # use system to find other sprite coordinates
            x = option.x()
            y = option.y()
        self._x = x
        self._y = y

    def glide_seconds_to_x_y(self, x, y, seconds):
        # work - do replace 'glide' with a 'for loop + goto'
        self._x = x
        self._y = y

    def point_in_direction(self, direction):
        self._direction = ( ( direction + 179 ) % 360 ) - 179
        self._update_sprite()

    def point_towards(self, option):
        if option == "mouse_pointer":
            # use system to find mouse coordinates
            target_x = self._project.sensing.mouse_x()
            target_y = self._project.sensing.mouse_y()
        else:
            # use system to find other sprite coordinates
            target_x = option.x()
            target_y = option.y()
        x = target_x - self._x
        y = target_y - self._y
        if x == 0 or y == 0:
            init_angle = 90
        else:
            init_angle = v.atan(x / y)
        if y <= 0:
            init_angle += 180
        angle = init_angle
        self.point_in_direction(angle)

    def change_x_by(self, x):
        self._x += x
        self._update_position()

    def set_x_to(self, x):
        self._x = x
        self._update_position()

    def change_y_by(self, y):
        self._y += y
        self._update_position()

    def set_y_to(self, y):
        self._y = y
        self._update_position()

    def if_on_edge_bounce(self): # not straightforward
        pass

    def set_rotation_style(self, option): # all around/left-right/dont rotate
        self._rotation_style = option

    # looks
    def say_for_seconds(self, message, seconds): # use global function?
        pass

    def say(self, message):
        pass

    def think_for_seconds(self, thought, seconds):
        pass

    def think(self, thought):
        pass

    def switch_costume_to(self, costume): # type function not correct
        if type(costume) == "int":
            self._switch_costume_to_num(costume)
        elif type(costume) == "str":
            try:
                self._switch_costume_to_str(costume)
            except ValueError:
                self._switch_costume_to_num(int(float(costume)))
        self._update_sprite()

    def next_costume(self):
        self._costume_number += 1
        if self._costume_number > len(self._costumes)-1:
            self._costume_number = 0
        self._update_sprite()

    def change_size_by(self, percentage):
        new_size = (self._size + percentage, )
        self.set_size_to(new_size)

    def set_size_to(self, percentage):
        self._size = percentage
        if self._size < 1:
            self._size = 1
        self._update_sprite()

    def change_look_effect_by(self, effect, value):
        pass

    def set_look_effect_to(self, effect, value):
        pass

    def clear_graphic_effects(self):
        pass

    def show(self):
        self._visible = True
        self._update_sprite()

    def hide(self):
        self._visible = False
        self._update_sprite()

    def go_to_front_layer(self):
        pass

    def go_to_back_layer(self):
        pass

    def go_forward_layers(self, layers):
        pass

    def go_backward_layers(self, layers):
        pass

    # sound
    def play_sound_until_done(self, sound):
        pass

    def play_sound(self, sound):
        pass

    def change_sound_effect_by(self, option, value): # pitch/pan left-right, value
        pass

    def set_sound_effect_to(self, option, value): # pitch/pan left-right, value
        pass

    def clear_sound_effects(self):
        pass

    def change_volume_by(self, percentage):
        pass

    def set_volume_to(self, percentage):
        pass

    def clone(self):
        attributes = self._package_attributes_for_clone()
        temp_sprite_parent = sprite.Sprite(**atributes)
        return temp_sprite_parent

    def delete(self):
        self._canvas.canvas.delete(self._tk_img)

    def touching(self, option): # work on this
        if option == 'mouse_pointer':
            pass

    def touching_colour(self, colour):
        pass

    def touching_color(self, color):
        pass

    def colour_is_touching_colour(self, colour1, colour2):
        pass

    def color_is_touching_color(self, color1, color2):
        pass

    def ask_and_wait(self, question):
        pass

    def set_drag_mode(self, option):
        if option == 'draggable':
            self._draggable = True
        elif option == 'not_draggable':
            self._draggable = False

    def loudness(self):
        return self._loudness





    ### NOT BUILT INS ###

    # bindings

    def _set_bindings(self):
        self._canvas.canvas.tag_bind(self._canvas_img, '<Button-1>', self._binding_clicked)

        self._canvas.canvas.tag_bind(self._canvas_img, '<Enter>', self._binding_mouse_enter)

        self._canvas.canvas.tag_bind(self._canvas_img, '<Leave>', self._binding_mouse_leave)

    def _binding_clicked(self, event):
        self._project.events.send_sprite_clicked_event(self._sprite_parent)

    def _binding_mouse_enter(self, event):
        self._touching_mouse = True

    def _binding_mouse_leave(self, event):
        self._touching_mouse = False

    # clone packaging attributes

    def _package_attributes_for_clone(self):
        attribute_dictionary = {
            'project':          self._project,
            # sprite_parent is added in 'clone' function
            'layer_order':      self._layer_order,
            'is_clone':         True,
            'visible':          self._visible,
            'draggable':        self._draggable,
            'rotation_style':   self._rotation_style,
            'costumes':         self._costumes,

            'x':                self._x,
            'y':                self._y,
            'direction':        self._direction,
            'size':             self._size,
            'costume_number':   self._costume_number,
            'volume':           self._volume,
            'answer':           self._answer
        }
        return attribute_dictionary

    # appearance updates

    def _find_index_of_dictionary_in_list_with_key_that_has_value(self, list_of_dictionaries, key, value):
        for index, dictionary in enumerate(list_of_dictionaries):
            if dictionary[key] == value:
                return index
        raise ValueError

    def _switch_costume_to_str(self, costume):
        costume_dictionary_index = self._find_index_of_dictionary_in_list_with_key_that_has_value(self._costumes, "name", costume)
        index = costume_dictionary_index+1
        self._costume_number = index

    def _switch_costume_to_num(self, costume):
        if costume in range(len(self._costumes)):
            self._costume_number = costume
        else:
            self._costume_number = costume % len(self._costumes)

    def _update_position(self):
        x = self._x + 240
        y = 180 - self._y
        self._canvas.canvas.coords(self._canvas_img, x, y)

    def _update_size(self):
        multiplier = self._size * 0.005
        current_width = self._pil_img.size[0]
        current_height = self._pil_img.size[1]
        new_width = current_width*multiplier
        new_height = current_height*multiplier
        new_size = (int(float(new_width)), int(float(new_height)))
        self._pil_img_edited = self._pil_img.resize(new_size)

    def _update_costume(self):
        self._pil_img = Image.open(self._costumes[int(self._costume_number)-1]["file"])


    def _update_rotation(self):
        if self._rotation_style == "all around":
            self._pil_img_edited = self._pil_img_edited.rotate(int(0-self._direction)+90, expand=1, resample=Image.BICUBIC)
        elif self._rotation_style == "dont rotate":
            pass
        elif self._rotation_style == "left-right":
            if self._direction < 0:
                self._pil_img_edited = self._pil_img_edited.transpose(Image.FLIP_LEFT_RIGHT)

    def _update_sprite(self):
        if self._visible:
            self._update_costume()
            self._update_size()
            self._update_rotation()
            self._tk_img = ImageTk.PhotoImage(self._pil_img_edited)
            self._canvas.canvas.itemconfig(self._canvas_img, image=self._tk_img, state="normal")
        else:
            self._canvas.canvas.itemconfig(self._canvas_img, state="hidden")