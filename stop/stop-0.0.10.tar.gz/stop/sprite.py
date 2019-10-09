from . import sprite_code
from . import scratch_math as v

path = "{0}/../assets/".format(__file__) # replace with prefs file

class Sprite:
    def __init__(self, project, parameters):
        self.project = project

        parameters = {
                'project':project,
                'sprite_parent':self,
                'is_clone': False,
                'layer_order':1, 
                'visible':True, 
                'draggable':False,
                'rotation_style':'all around',
                'costumes':[
                    {"file":"{0}costume1.png".format(path), "name":"costume1"}, 
                    {"file":"{0}costume2.png".format(path), "name":"costume2"}
                ],
                'x':0,
                'y':0,
                'size':100,
                'direction':90,
                'costume_number':0,
                'volume':100,
                'answer':'',
                **parameters
            }
            
        self.sprite_code = sprite_code.SpriteCode(parameters)
        

    def __getattr__(self, name):
        def wrapper(*args):
            function_name = name
            function_arguements = args
            self._add_instruction_to_queue(function_name, *function_arguements)
        return wrapper

    def _add_instruction_to_queue(self, block, *parameters):
        item_function = getattr(self.sprite_code, block)
        item = {
            'function': item_function,
            'parameters': parameters
        }
        self.project.add_instruction_to_queue(item)

    
    # return functions

    def touching_mouse(self):
        return self.sprite_code._touching_mouse

    def x(self):
        return self.sprite_code._x

    def y(self):
        return self.sprite_code._y

    def direction(self):
        return self.sprite_code._direction

    def size(self):
        return self.sprite_code._size

    def costume_name(self):
        return self.sprite_code._costumes[self.costume('number')]['name']

    def costume_number(self):
        return self.sprite_code._costume_number

    def volume(self):
        return self.sprite_code._volume

    def distance_to(self, option):
        x1 = self.x()
        y1 = self.y()
        if option == 'mouse_pointer':
            x2 = self.project.mouse_x
            y2 = self.project.mouse_y
        else: # must be sprite
            x2 = option.x()
            y2 = option.y()
        dx = x2 - x1
        dy = y2 - y1
        distance = v.sqrt(v.add(v.mul(dx, dx), v.mul(dy, dy)))
        return distance

    def answer(self):
        return self.sprite_code._answer