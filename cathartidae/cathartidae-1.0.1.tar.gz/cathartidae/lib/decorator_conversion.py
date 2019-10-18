def convert_to_decorator(type_of_decorator, block, operand, *args):
    DecoratorConstructor = type_of_decorator
    def control_decorator(func):
        return DecoratorConstructor(block, operand, func, *args)
    return control_decorator
