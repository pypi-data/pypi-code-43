import json
from . import sprite
from .prefs import prefs

def generate_code(json_string):
    json_dictionary = json.loads(json_string)

    sprites_code_list = []

    for target_index in range(len(json_dictionary['targets'])):
        if json_dictionary['targets'][target_index]['isStage'] == False:
            temporary_sprite = sprite.Sprite(json_dictionary, target_index)
            sprite_code = temporary_sprite.generate_code()
            sprites_code_list.append(sprite_code)

    sprite_code = '\n\n\n'.join(sprites_code_list)



    code = '''import stop
{0} = stop.Project()

{1}

{0}.run()

    '''.format(
        prefs['project_variable_name'],
        sprite_code
    )

    return code









# generate oop structure
# sprite > scripts > block