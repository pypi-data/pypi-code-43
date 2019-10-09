from abc import ABC, abstractmethod


class CompositPatternABC(ABC):

    def __init__(self):
        super(CompositPatternABC, self).__init__()

        self._data = None

    @property
    @abstractmethod
    def data(self):
        return NotImplementedError('Not implemented')

class SimpleDynamicClass(CompositPatternABC):

    def __init__(self, data):
        super(SimpleDynamicClass, self).__init__()

        self._data = data

    @property
    def data(self):
        return self._data

class CompositeDynamicClass(CompositPatternABC):

    def __init__(self, data):

        super(CompositeDynamicClass, self).__init__()

        if isinstance(data, dict):

            for key, value in data.items():

                # print('key: ', key, ' type: ', type(value), ' value: ', value)

                if isinstance(value, dict) or isinstance(value, list):
                    # print('dict')
                    self.__dict__[key] = CompositeDynamicClass(value)

                else:
                    self.__dict__[key] = SimpleDynamicClass(value)

        elif isinstance(data, list):

            self._data = list()

            for item in data:
                if isinstance(item, dict) or isinstance(item, list):
                    self._data.append(CompositeDynamicClass(item))
                else:
                    self._data.append(SimpleDynamicClass(item))

    @property
    def data(self):

        if self._data is not None:
            return [item.data for item in self._data]

        return {key:value.data for (key,value) in self.__dict__.items() if key != '_data'}
