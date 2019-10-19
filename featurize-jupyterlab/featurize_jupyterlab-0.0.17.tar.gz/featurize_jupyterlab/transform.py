import collections
from .core import Dataflow, ComponentMeta, Option
from abc import abstractmethod


class Column:
    def __init__(self, name, multiple=False, required=False, description='', key=None):
        self.multiple = multiple
        self.name = name
        self.required = required
        self.description = description
        self.key = key


class Compose():

    def __init__(self, *transformations):
        self.transformations = list(transformations)

    def __call__(self, rowdata):
        for transformation in self.transformations:
            rowdata = transformation(rowdata)
        return rowdata

    def add(self, transformation):
        self.transformations.append(transformation)


class BasicTransformation(Dataflow):

    # 目前不支持配置 column，需要由子类写死配置
    # columns_config = Option(type='string', help='暂时不支持自选 Column')

    def __call__(self, rowdata):
        for column in self.columns_config:
            rowdata[column] = self.transform(rowdata[column])
        return rowdata

    @abstractmethod
    def transform(self, data):
        pass


class BasicImageTransformation(BasicTransformation):
    probability = Option(type='number', default=0.5)

    def initialize(self):
        self.aug = self.create_aug()

    def transform(self, image):
        return self.aug(image=image)['image']

    @abstractmethod
    def create_aug(self):
        pass


class MeaningfulColumnsTransformationMeta(ComponentMeta):
    def __new__(cls, clsname, bases, context):
        columns = []
        if len(bases) > 0:
            columns += getattr(bases[0], 'columns', [])

        for column_key, column in context.items():
            if isinstance(column, Column):
                column.key = column_key
                columns.append(column)
        context['columns'] = columns
        return super().__new__(cls, clsname, bases, context)

    @classmethod
    def __prepare__(cls, clsname, bases):
        return collections.OrderedDict()


class MeaningfulColumnsTransformation(BasicTransformation,
        metaclass=MeaningfulColumnsTransformationMeta):
    def __call__(self, row_data):
        parameters = {}
        for column in self.__class__.columns:
            if column.multiple:
                for key in self.columns_config.get(column.key, []):
                    if column.key not in parameters:
                        parameters[column.key] = []
                    parameters[column.key].append(row_data[key])
            else:
                try:
                    value = row_data[self.columns_config[column.key]]
                    parameters[column.key] = value
                except KeyError:
                    pass
        result = self.transform(**parameters)
        for column in self.__class__.columns:
            if column.multiple:
                for index, key in enumerate(self.columns_config.get(column.key, [])):
                    row_data[key] = result[column.key][index]
            else:
                try:
                    row_data[self.columns_config[column.key]] = result[column.key]
                except KeyError:
                    pass
        return row_data


class DualImageTransformation(MeaningfulColumnsTransformation):
    image = Column(name='image', required=True)
    mask = Column(name='mask', description='This column should be in run length encoded')
    masks = Column(name='masks', multiple=True, description='This column should be in run length encoded')
    keypoints = Column(name='key points', description='Points\' format (x, y) format. Multiple key points seperated by ","')
    bboxes = Column(name='bounding boxes', description='Boxes\' format is (top, left, width, height), seperated by ","')

    probability = Option(type='number')

    def initialize(self):
        self.aug = self.create_aug()

    def transform(self, **arguments):
        return self.aug(**arguments)

    @abstractmethod
    def create_aug(self):
        pass
