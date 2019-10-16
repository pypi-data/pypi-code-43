'''
封装mysql 查询对象
'''
from enum import Enum
from com.fw.utils.common_utils import CommonUtils

class QueryLogical(Enum):
    IS = '等于'
    NIS = '不等于'
    LIKE_ALL = 'like'
    IN = '在'
    NOT_IN = '不在..'
    LIKE_LEFT = '左like'
    LIKE_RIGHT = '右like'
    GT = '大于'
    GTE = '大于等于'
    LT = '小于'
    LTE = '小于等于'


class Sud(Enum):
    ASC = '升序'
    DESC = '倒序'


class Criteria(object):
    def __init__(self, key, value, queryLogical: QueryLogical):
        self.key = key
        self.queryLogical = queryLogical
        self.value = value


class Page(object):
    def __init__(self, to_page=1, page_size=10):
        if to_page < 1 or page_size <= 0:
            raise BaseException('PAGE PARAMS ERROR')

        self.to_page = to_page
        self.page_size = page_size


class Sort(object):
    def __init__(self, key: str, sud: Sud):
        self.key = key
        self.sud = sud


class QueryUtils(object):

    def __init__(self):
        self.criterias = []
        self.page = Page(1, 10)
        self.sort = None
        self._index = {}

    def add_criteria(self, key, value, queryLogical: QueryLogical = QueryLogical.IS):
        self._index[key] = len(self.criterias)
        self.criterias.append(Criteria(key, value, queryLogical))

    def add_page(self, to_page=1, page_size=10):
        self.page = Page(to_page, page_size)

    def add_sort(self, sort_filed: str, sud: Sud):
        self.sort = Sort(sort_filed, sud)

    def set_criteria_logical(self, key, queryLogical: QueryLogical):
        self.criterias[self._index[key]].queryLogical = queryLogical

    @staticmethod
    def dict_to_query(param: dict):
        query = QueryUtils()

        if "to_page" in param.keys() and "page_size" in param.keys():
            query.add_page(int(param["to_page"]), int(param["page_size"]))
            param.pop("to_page")
            param.pop("page_size")

        if "sort_filed" in param.keys() and "sud" in param.keys():
            query.add_page(param["sort_filed"], param["sud"])
            param.pop("sort_filed")
            param.pop("sud")


        for key, val in param.items():
            if key == "req_id" or key == "t_conn" or CommonUtils.isEmpty(val):
                continue
            query.add_criteria(key, val)

        return query
