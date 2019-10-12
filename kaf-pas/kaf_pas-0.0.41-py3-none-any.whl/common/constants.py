from enum import Enum, IntEnum


class constants1:
    documentation = 5
    complex = 10
    assembly_units = 15
    minutiae = 20
    standard_products = 25
    other_products = 30
    materials = 35
    kits = 40

    # spcObjType - тип объектов:
    # 0 - базовые,
    # 1 - вспомогательные,
    # 2 - базовые и вспомогательные из сортирован­ного массива,
    # 3 - все объекты.

    spcObjTypeBase = 0
    spcObjTypeAuxiliary = 1
    spcObjTypeBaseAuxiliarySorted = 2
    spcObjTypeAll = 3

    # ksMoveIterator - направление перемещения итератора:
    ksMoveIteratorF = 'F'  # - первый объект,
    ksMoveIteratorN = 'N'  # - следующий объект.

    # additioanalCol - признак колонок:

    additioanalColTable = 0  # - колонки таблицы спецификации,
    additioanalColAdded = 1  # - дополнительныеколонки


class specRow:
    format = None
    zone = None
    pos = None
    mark = None
    name = None
    count = None
    note = None
    massa = None
    material = None
    user = None
    code = None
    factory = None
    complex = None


class ColumnType(IntEnum):
    SPC_CLM_FORMAT = 1  # Формат
    SPC_CLM_ZONE = 2  # Зона
    SPC_CLM_POS = 3  # Позиция
    SPC_CLM_MARK = 4  # Обозначение
    SPC_CLM_NAME = 5  # Наименование
    SPC_CLM_COUNT = 6  # Количество
    SPC_CLM_NOTE = 7  # Примечание
    SPC_CLM_MASSA = 8  # Масса
    SPC_CLM_MATERIAL = 9  # Материал
    SPC_CLM_USER = 10  # Пользовательская
    SPC_CLM_KOD = 11  # Код
    SPC_CLM_FACTORY = 12  # Предприятие - изготовитель


class FormatsRastr(IntEnum):
    FORMAT_BMP = 0 #- BMP,
    FORMAT_GIF = 1 #- GIF,
    FORMAT_JPG = 2 #- JPEG,
    FORMAT_PNG = 3 #- PNG,
    FORMAT_TIF = 4 #- TIFF,
    FORMAT_TGA = 5 #- TGA,
    FORMAT_PCX = 6 #- PCX
    #FORMAT_WMF = 16 #- WMF(неподдерживается)
    FORMAT_EMF = 17 #- EMF

class DeepOfColer(IntEnum):
    BPP_COLOR_01 = 1 #- монохромный,
    BPP_COLOR_02 = 2 #- 4 цвета,
    BPP_COLOR_04 = 4 #- 16 цветов,
    BPP_COLOR_08 = 8 #- 256 цветов,
    BPP_COLOR_16 = 16 #- 16 разрядов,
    BPP_COLOR_24 = 24 #- 24 разряда,
    BPP_COLOR_32 = 32 #- 32 разряда.

class Color4OutObj(IntEnum):
    BLACKWHITE = 0 #- черный,
    COLORVIEW = 1 #- цвет, установленный для вида,
    COLORLAYER =  2 #- цвет, установленный для слоя,
    COLOROBJECT = 3 #- цвет, установленный для объекта.






