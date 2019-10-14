
def _create_class(name:str, superclasses:tuple, properties:dict):
    new_class = type(name, superclasses, properties)

    for k,v in properties.items():
        if 'dict' in str(type(v)):
            another_class = _create_class(k,(),v)
            setattr(new_class,k, another_class)
    return new_class


class_name = "MainClass"
super_class= tuple()
def load(json_dictionary):
    result = _create_class(class_name,(super_class), json_dictionary)
    return result












