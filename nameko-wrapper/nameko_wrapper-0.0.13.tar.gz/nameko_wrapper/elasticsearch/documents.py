"""
Document Extend
"""
import datetime
import warnings

from elasticsearch_dsl import Document, Q, connections, Search, Index
from elasticsearch.exceptions import NotFoundError

from .exceptions import (UniqueException, UniqueTogetherException, ServiceErrorException, MultiObjectReturnException)
from nameko_wrapper.exceptions import ObjectDoesNotExist


class ExtendDocument(Document):
    """Extend ElasticSearch Document"""

    class Extend:
        """扩展参数配置
        Parameters:
            unique/unique_together 仅对关键字类型（Keyword)起作用，如果非关键字类型则直接跳过

            unique: str/list/tuple 唯一字段
            unique_together: iter   要求一起唯一
            auto_now_fields: 当对象使用save时自动更新为当前时间
            auto_now_add_fields: 当对象首次创建时更新为当前时间
        """
        unique = ''
        unique_together = []
        auto_now_fields = []
        auto_now_add_fields = []


    def _get_extend_settings(self):
        """获取extend参数"""
        return {
            key: getattr(self.Extend, key)
            for key in dir(self.Extend)
            if not key.startswith('__') and not callable(getattr(self.Extend, key)) and getattr(self.Extend, key)
        }

    @classmethod
    def get_document_index(cls):
        """获取文档索引"""
        return cls._index

    @classmethod
    def get_document_mapping_dict(cls, attrs_list=None):
        """获取文档Mapping

        Args:
            attrs_list: 属性列表 None/list
        """
        index = cls.get_document_index()
        index_name = index._name
        index_type = index._get_doc_type()
        index_mappings = index.get_mapping()

        # 获取mapping
        _mappings = index_mappings[index_name]['mappings'][index_type]['properties']
        if not attrs_list:
            return _mappings
        else:
            return {attr: _mappings[attr] for attr in attrs_list if attr in _mappings}

    @classmethod
    def get_type_attrs(cls, attr_type, attrs_list=None, recurse=True):
        """获取指定类型属性名列表

        Args:
            attr_type: elasticsearch 属性类型（小写）
            attrs_list: 属性列表，当为None时从全部属性获取，为列表时获取列表的属性
            recurse: 是否递归进行查找

        Returns:
            满足type类型的属性名列表，如果是`multi-fields`类型将会返回`attr.field_name`形式

        Warnings:
            如果没有功能问题，请不要试着修改此函数，程序可能比较难理解，使用递归实现
        """
        attr_dict = cls.get_document_mapping_dict()

        def _get_type_attrs(attr_obj, _attr_type, _attrs_list, _recurse):
            """
            获取指定`type`类型的属性，包括`multi-fields`属性
            Args:
                attr_obj:
                _attr_type:
                _attrs_list:
                _recurse:
                以上参数是此类方法的参数值，为了将函数变量包含在局部环境内

            Returns:
                满足type类型的属性名列表，如果是`multi-fields`类型将会返回`attr.field_name`形式
            """
            attr_names_list = []
            attr_name = []

            def _get_type_attr_from_dict(_attr_dict, attr_name):
                for attr, value in _attr_dict.items():
                    if ((_attrs_list and attr in _attrs_list) or attr_name) or _attrs_list is None:
                        if value['type'] == _attr_type:
                            # print('type == attr_type')
                            attr_name.append(attr)
                        else:
                            if _recurse and 'fields' in value:
                                # print('call type attr from dict > 1 times.')
                                attr_name_sub = attr_name.copy()
                                attr_name_sub.append(attr)
                                _get_type_attr_from_dict(value['fields'], attr_name_sub)

                            continue
                        # print('attr_names_list append string list:', attr_name)
                        attr_names_list.append('.'.join(attr_name))
                        attr_name.clear()   # 清空列表

            _get_type_attr_from_dict(attr_obj, attr_name=attr_name)
            return attr_names_list

        return _get_type_attrs(attr_dict, attr_type, attrs_list, recurse)

    def _get_unique_keyword_list(self, unique_attrs):
        """检查关键字属性，返回过滤后的列表

        """
        if unique_attrs:
            return self.get_type_attrs('keyword', unique_attrs)
        else:
            return None

    def _check_term_unique(self, term, term_value):
        """检查term查询是否存在，返回True/False"""
        search_result = self.search().query('term', **{term: term_value}).execute()
        if search_result.hits.total > 0:
            if getattr(self, 'meta', None) and getattr(self.meta, 'id', None):
                # 判断当前id是否存在于查询结果中，存在这跳过
                # print(search_result.hits.hits)
                for hit in search_result.hits.hits:
                    if hit['_id'] == self.meta.id:
                        if search_result.hits.total > 1:
                            warnings.warn(f'unique field {term} exists {search_result.hits.total} repeat record.')
                        return True

            return False
        else:
            return True

    def _check_terms_unique_together(self, terms):
        """检查多个terms查询是否唯一存在"""
        if terms:
            query_list = []
            for term in terms:
                query_list.append(Q('term', **{term: getattr(self, term.split('.')[0])}))
            q = Q('bool', must=query_list)
            # print(q.to_dict(), self.search().query(q).execute().hits.total)
            if self.search().query(q).execute().hits.total > 0:
                return False
            else:
                return True
        return None

    def unique_together_check(self):
        """"""
        pass

    def _check(self, args, kwargs, *, is_update=False):
        """检查限制条件"""

        extend_settings = self._get_extend_settings()
        # print(extend_settings)

        if 'unique' in extend_settings:
            # 获取unique属性列表
            unique_attrs = (extend_settings['unique']
                            if isinstance(extend_settings['unique'], list) or isinstance(extend_settings['unique'],
                                                                                         tuple)
                            else [extend_settings['unique']])

            # 判断对象是否为关键字类型属性
            unique_attrs = self._get_unique_keyword_list(unique_attrs)

            # 依次判断属性是否存在和结果是否已经存在
            if unique_attrs:
                for attr in unique_attrs:
                    term_name = attr.split('.')[0]
                    if attr in self or term_name in self:
                        term_value = kwargs.get(term_name) if is_update else getattr(self, term_name, None)
                        if is_update and term_value == getattr(self, term_name, None):
                            pass
                        else:
                            if not self._check_term_unique(term=attr, term_value=term_value):
                                # 引发异常跳过后面检查
                                raise UniqueException('文档创建时发生冲突'.format(attr))

        if 'unique_together' in extend_settings:
            # 判断多个字段的唯一性
            unique_attrs = extend_settings['unique_together']

            # 判断属性是否都存在，如果都存在才有效，否则直接引发异常
            for attr in unique_attrs:
                if attr not in self:
                    raise UniqueTogetherException('唯一条件内容缺失，无效的创建请求！')

            new_unique_attrs = self._get_unique_keyword_list(unique_attrs)
            if new_unique_attrs and len(new_unique_attrs) == len(unique_attrs):
                if not self._check_terms_unique_together(new_unique_attrs):
                    raise UniqueTogetherException('类似文档已存在，无法创建新的文档')
            else:
                raise ValueError('`unique_together`可迭代参数列表必须都为`Keyword`或`Keyword`型Text类型字段名或不能为空')

        if 'auto_now_add_fields' in extend_settings and not is_update:
            self._auto_now_add_fields_action(extend_settings['auto_now_add_fields'], kwargs, is_update=is_update)

        # 从kwargs中移除auto now add fields
        if is_update:
            self._remove_auto_time_fields(extend_settings['auto_now_add_fields'], kwargs, is_update)

        if 'auto_now_fields' in extend_settings:
            self._auto_now_fields_action(extend_settings['auto_now_fields'], kwargs, is_update=is_update)

    def save(self, *args, is_check=True, **kwargs):
        """保存时根据不同扩展参数进行判断

        Args:
            is_check: bool 保存时是否进行条件检查
        """
        # print('# document save:', self, dir(self), args, is_check, kwargs)
        if is_check:
            self._check(args, kwargs)

        return super().save(*args, **kwargs)

    def update(self, *args, is_check=True, **kwargs):
        """document update"""
        # print('# document update:', self, dir(self), is_check, kwargs)
        if is_check:
            self._check(args, kwargs, is_update=True)

        # print(self, self.updated_time, kwargs, args)
        return super().update(*args, **kwargs)

    def _check_fields_type(self, fields, field_type, *, raise_exception=True):
        """检查fields是否为列表且存在于document mapping之中"""
        if not any(map(lambda x: isinstance(fields, x), [list, tuple, set])):
            return False

        mapping = self.get_document_mapping_dict()

        not_exist_fields = []
        type_error_fields = []
        for field in fields:
            if field not in mapping:
                not_exist_fields.append(field)
            else:
                if mapping[field]['type'] != field_type:
                    type_error_fields.append(field)

        if len(not_exist_fields) == 0 and len(type_error_fields) == 0:
            return True
        else:
            if raise_exception:
                raise ServiceErrorException(
                    f"{','.join(not_exist_fields)} total {len(not_exist_fields)} not exist in mapping, "
                    f"{','.join(type_error_fields)} total {len(type_error_fields)} not match field type `{field_type}`."
                )
            else:
                return False

    def _remove_auto_time_fields(self, fields, kwargs, is_update):
        """从kwargs中移除fields"""
        if is_update:
            # 更新文档
            i = map(lambda x: kwargs.pop(x, None), fields)
            list(i)
        else:
            # 当文档创建时，未保存文档时，删除所有用户记录
            for field in fields:
                if not getattr(self, 'meta', None):
                    setattr(self, field, None)

    def _fields_auto_add_current_time(self, fields, kwargs, is_cover=False, is_update=False):
        """自动添加当前时间"""
        for field in fields:
            if getattr(self, field, None):
                if not is_cover:
                    # 删除属性
                    if not is_update:
                        try:
                            delattr(self, field)
                        except AttributeError:
                            pass
                    continue

            if is_update:
                kwargs[field] = datetime.datetime.now()
            else:
                if getattr(self, 'meta', None):
                    setattr(self, field, datetime.datetime.now())

    def __auto_set_datetime(self, fields, kwargs, *, is_once=True, is_update):
        """自动设置更新时间"""
        self._check_fields_type(fields, field_type='date')
        # 移除用户输入
        self._remove_auto_time_fields(fields, kwargs, is_update)
        # 自动添加时间
        self._fields_auto_add_current_time(fields, kwargs, is_cover=not is_once, is_update=is_update)

    def _auto_now_fields_action(self, fields, kwargs, *, is_update=False):
        """每次保存时自动更新时间"""
        self.__auto_set_datetime(fields, kwargs, is_once=False, is_update=is_update)

    def _auto_now_add_fields_action(self, fields, kwargs, *, is_update=False):
        """每次创建时保存一次"""
        self.__auto_set_datetime(fields, kwargs, is_once=True, is_update=is_update)

    def get_document_dict(self):
        """在用户保存后，获取用户属性字典

        Warnings:
            此方法不适合在document保存后调用，因为此时文档可能出现无法搜索的问题
        """
        # 判断用户是否已经保存
        if 'id' in self.meta:
            # print(self.__class__.get_document_by_id(self.meta.id))
            return self.__class__.term_query_search_by_id(self.meta.id)
        else:
            # 提示当前文档还未保存
            raise ServiceErrorException("Current document object doesn't save, can't get document id.")

    @classmethod
    def get_document_by_id(cls, document_id, *, raise_exception=False):
        """通过文档ID获取文档

        Args:
            document_id: 文档ID
            raise_exception: 是否触发异常
        """
        try:
            doc = cls.get(id=document_id)
        except NotFoundError:
            if raise_exception:
                raise ObjectDoesNotExist
            else:
                return None
        else:
            return doc

    @classmethod
    def update_document(cls, id, data):
        es = connections.get_connection()
        es.update(index=cls.Index.name, doc_type='doc', id=id, body={'doc': data})

    @staticmethod
    def _search_item_to_dict(search_item):
        """将搜索项转换为字典"""
        item_content = search_item['_source']
        print(item_content)
        if 'id' not in item_content:
            # raise ServiceErrorException('无法正确插入id')
            item_content['id'] = search_item['_id']
        return item_content

    @staticmethod
    def get_dict_list_from_search_result(search_result):
        """从搜索结果获取字典"""
        result = search_result.hits.hits
        if len(result) > 0:
            return [ExtendDocument._search_item_to_dict(item) for item in result]
        else:
            return []

    @classmethod
    def term_query_search(cls, query_terms, *, to_dict=False):
        """通过查询字典进行查询"""
        query = Q()
        for term in query_terms:
            query &= Q('term', **{term: query_terms[term]})

        print(query.to_dict())
        search = Search(index=cls.Index.name).query(query)
        result = search.execute()

        if to_dict:
            return cls.get_dict_list_from_search_result(result)
        else:
            return result.hits.hits

    @classmethod
    def term_query_search_by_id(cls, id, *, to_dict=True):
        result = cls.term_query_search({'_id': id}, to_dict=to_dict)
        if result:
            return result[0]
        else:
            return None

    @classmethod
    def get_document_by_term_search(cls, query_term, raise_exception=False):
        documents = cls.term_query_search(query_terms=query_term, to_dict=True)
        if not len(documents):
            if raise_exception:
                raise ObjectDoesNotExist
            else:
                return None
        elif len(documents) > 1:
            raise MultiObjectReturnException
        else:
            return cls.get_document_by_id(documents[0]['id'])


def init_document_index(document_cls, connection=None, *, delete_on_conflict=False):
    """初始化文档索引

    判断当前库是否存在同名的Index，不存在则进行初始化

    Args:
        document_cls: 文档类
        connection: es连接
        delete_on_conflict: 是否当冲突时删除重建
    """

    if connection:
        c = connection
    else:
        try:
            c = connections.get_connection()
            print(c)
        except KeyError as e:
            raise ServiceErrorException("No find a valid connection.")

    indexes_dict = c.indices.get_alias()
    index_names = tuple(indexes_dict.keys())
    index_alias_names = []
    for index in indexes_dict:
        index_alias_names.extend(list(indexes_dict[index]['aliases'].keys()))
    index_alias_names = tuple(index_alias_names)

    # print(index_names, index_alias_names)

    # 获取文档类的索引名称
    try:
        document_index_name = document_cls.Index.name
    except AttributeError:
        raise AttributeError("Document `{}` does't have `Index.name` attribute".format(document_cls))
    else:
        # 判断索引是否已存在
        if document_index_name in index_names or document_index_name in index_alias_names:
            print('document `{}` index exist.'.format(document_index_name))
            if delete_on_conflict:
                Index(name=document_index_name, using=c).delete()
                print('[Conflict Delete]: document `{}` index deleted.'.format(document_index_name))
            else:
                return

        document_cls.init()
        print('document `{}` index created.'.format(document_index_name))
