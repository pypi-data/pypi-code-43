# -*- coding:utf-8 -*-  
# __auth__ = mocobk
# email: mailmzb@qq.com

from collections import namedtuple

TAG_META = '__tag__'
LEVEL_META = '__level__'


def tag(*tag_type):
    """
    指定测试用例环境标签，支持同时设定多个标签，默认Tag.ALL
    :param tag_type: Tag obj
    :return: function
    e.g.
        @tag(Tag.TEST, Tag.PROD)
        def test_method(self):
            pass
    """

    def wrap(func):
        if not hasattr(func, TAG_META):
            tags = {Tag.ALL}
            tags.update(tag_type)
            setattr(func, TAG_META, tags)
        else:
            getattr(func, TAG_META).update(tag_type)
        return func

    return wrap


def level(_level):
    """
    指定测试用例环境标签，支持同时设定多个标签，默认Tag.ALL
    :param _level: Level obj
    :return: function
    e.g.
        @level(Level.P1)
        def test_method(self):
            pass
    """

    def wrap(func):
        if not hasattr(func, LEVEL_META):
            setattr(func, LEVEL_META, _level)
        else:
            __level = getattr(func, LEVEL_META)
            setattr(func, LEVEL_META, min([_level, __level], lambda x: int(x)))
        return func

    return wrap


class NewTag:
    def __init__(self, desc=""):
        self.desc = desc


class NewLevel:
    def __init__(self, value, desc=""):
        self.value = value
        self.desc = desc

    def __int__(self):
        return self.value


class Tag:
    DEV = NewTag('Development')
    TEST = NewTag('Testing')
    UAT = NewTag('User Acceptance Test')
    SIM = NewTag('Simulation')
    PROD = NewTag('Production')
    ALL = NewTag("ALL")

    RUN_TAG = {ALL}
    DEFAULT = {ALL, DEV, TEST, UAT, SIM, PROD}

    @classmethod
    def set_run_tag(cls, *tag_type):
        cls.RUN_TAG = set(tag_type)


class Level:
    SMOKE = NewLevel(0, 'Smoke')
    P0 = NewLevel(0, 'P0')
    P1 = NewLevel(10, 'P1')
    P2 = NewLevel(20, 'P2')
    P3 = NewLevel(30, 'P3')
    P4 = NewLevel(40, 'P4')

    RUN_LEVEL = P4
    DEFAULT = P0

    @classmethod
    def set_run_level(cls, _level):
        cls.RUN_LEVEL = _level


def _tag_decorator(_tag):
    def wrap(func):
        if not hasattr(func, TAG_META):
            # 给一个默认的 ALL tag 未设置运行 tag 时则都不跳过
            tags = {Tag.ALL}
            tags.update(_tag)
            setattr(func, TAG_META, tags)
        else:
            getattr(func, TAG_META).update(_tag)
        return func

    return wrap


def _level_decorator(_level):
    def wrap(func):
        if not hasattr(func, LEVEL_META):
            setattr(func, LEVEL_META, _level)
        else:
            __level = getattr(func, LEVEL_META)
            setattr(func, LEVEL_META, min([_level, __level], lambda x: int(x)))
        return func

    return wrap


class Meta(type):
    def __new__(mcs, cls_name, bases, attr_dict: dict):
        items = list(attr_dict)
        run_tag = set(Tag.RUN_TAG)
        run_level = int(Level.RUN_LEVEL)
        skip_tag_reason = '\n执行环境非 {}'
        skip_level_reason = '\n用例执行优先级小于 {}'
        for item in items:
            if item.startswith('test'):
                if not hasattr(attr_dict[item], TAG_META):
                    setattr(attr_dict[item], TAG_META, Tag.DEFAULT)
                # 获取交集
                if not getattr(attr_dict[item], TAG_META) & run_tag:
                    setattr(attr_dict[item], '__unittest_skip__', True)
                    skip_reason = getattr(attr_dict[item], '__unittest_skip_why__', '')
                    setattr(attr_dict[item], '__unittest_skip_why__', (skip_reason + skip_tag_reason.format(
                        [item.desc for item in getattr(attr_dict[item], TAG_META)])).strip())

                if not hasattr(attr_dict[item], LEVEL_META):
                    setattr(attr_dict[item], LEVEL_META, Level.DEFAULT)
                if int(getattr(attr_dict[item], LEVEL_META)) > run_level:
                    setattr(attr_dict[item], '__unittest_skip__', True)
                    skip_reason = getattr(attr_dict[item], '__unittest_skip_why__', '')
                    setattr(attr_dict[item], '__unittest_skip_why__',
                            (skip_reason + skip_level_reason.format(Level.RUN_LEVEL.desc)).strip())

        return super(Meta, mcs).__new__(mcs, cls_name, bases, attr_dict)


class _Filter:
    _ENV_MAP = {
        'TEST': Tag.TEST,
        'UAT': Tag.UAT,
        'PROD': Tag.PROD,
        'PRODUCTION': Tag.PROD,
    }
    _LEVEL_MAP = {
        'SMOKE': Level.SMOKE,
        'P0': Level.P0,
        'P1': Level.P1,
        'P2': Level.P2,
        'P3': Level.P3,
        'P4': Level.P4,
    }
    Meta = Meta

    def __init__(self):
        self._env = None
        self._level = 'p4'

    @property
    def env(self):
        return self._env

    @env.setter
    def env(self, value: str):
        self._env = value
        Tag.set_run_tag(self._ENV_MAP.get(value.upper(), Tag.ALL))

    @property
    def level(self):
        return self._level

    @level.setter
    def level(self, value: str):
        self._level = value
        Level.set_run_level(self._LEVEL_MAP.get(value.upper(), Level.P4))


Filter = _Filter()

names = namedtuple('flag', ['env', 'level_in'])
env = namedtuple('env', ['TEST', 'UAT', 'PROD', 'NOT_TEST', 'NOT_UAT', 'NOT_PROD'])
levels = namedtuple('levels', ['SMOKE', 'P0', 'P1', 'P2', 'P3', 'P4'])

runIf = names(
    env=env(
        TEST=_tag_decorator(_tag={Tag.TEST}),
        UAT=_tag_decorator(_tag={Tag.UAT}),
        PROD=_tag_decorator(_tag={Tag.PROD}),
        NOT_TEST=_tag_decorator(_tag={Tag.UAT, Tag.PROD}),
        NOT_UAT=_tag_decorator(_tag={Tag.TEST, Tag.PROD}),
        NOT_PROD=_tag_decorator(_tag={Tag.TEST, Tag.UAT}),
    ),
    level_in=levels(
        SMOKE=_level_decorator(Level.SMOKE),
        P0=_level_decorator(Level.P0),
        P1=_level_decorator(Level.P1),
        P2=_level_decorator(Level.P2),
        P3=_level_decorator(Level.P3),
        P4=_level_decorator(Level.P4),
    )
)
