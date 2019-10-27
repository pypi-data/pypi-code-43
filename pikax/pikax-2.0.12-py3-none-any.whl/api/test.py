class Parent:
    def __init__(self, param_id):
        print(f'Parent init {param_id}')

    @classmethod
    def factory(cls, param_id):
        return cls(param_id)


class Child(Parent):

    def __init__(self, my_id):
        super().__init__(my_id)
        print(f'Child init: {my_id}')


def main():
    child = Child.factory(123)
    print(type(child))


if __name__ == '__main__':
    main()
