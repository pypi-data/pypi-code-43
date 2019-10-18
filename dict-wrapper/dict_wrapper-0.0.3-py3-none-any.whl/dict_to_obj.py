
class DictWrapper:

    class Dict(dict):
        __setattr__ = dict.__setitem__
        __getattr__ = dict.__getitem__

    @staticmethod
    def wrapper(dictionary):
        if not isinstance(dictionary, dict):
            return dictionary
        obj = DictWrapper.Dict()
        for k, v in dictionary.items():
            obj[k] = DictWrapper.wrapper(v)
        return obj

    def __new__(cls, *args, **kwargs):
        return DictWrapper.wrapper(args[0])

if __name__ == '__main__':
    data = {
        "who": 'your name',
        "area": ['specify', 'china'],
        "province": {
            "city": ['shenzhen', 'guangzhou']
        }
    }
    config = DictWrapper(data)
    assert config.who == 'your name'
    assert config.province.city == ['shenzhen', 'guangzhou']
    print(config.area)
