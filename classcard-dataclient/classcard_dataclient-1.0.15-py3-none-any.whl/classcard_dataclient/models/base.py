from ..utils.exceptions import ValidateError


class BaseModel(object):
    def __init__(self, *args, **kwargs):
        self.required_filed = []
        for key, value in kwargs.items():
            setattr(self, key, value)

    def check_required(self):
        """
        检查必填字段是否填写了
        :return:
        """
        for nnf in self.required_filed:
            if getattr(self, nnf) is None:
                raise ValueError("{} must can't be null".format(nnf))

    def spe_validate(self):
        """
        自定义特殊检测
        :return:
        """
        pass

    def validate(self):
        """
        属性完整性检查
        :return:
        """
        try:
            self.check_required()
            self.spe_validate()
        except (Exception,) as e:
            raise ValidateError("{}".format(e))
        return True

    @property
    def nirvana_data(self):
        """
        班牌接口数据结构
        :return:
        """
        data = {}
        return data

    @property
    def sso_data(self):
        """
        用户中心接口数据结构
        :return:
        """
        data = {}
        return data
