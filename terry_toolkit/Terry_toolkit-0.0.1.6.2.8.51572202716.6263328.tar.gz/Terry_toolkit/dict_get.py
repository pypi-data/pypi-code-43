# coding: utf-8
import types

# 获取字典中的objkey对应的值，适用于字典嵌套
# dict:字典
# objkey:目标key
# default:找不到时返回的默认值


class Dict:
    """词典操作函数
    
    
    """
    def __init__(self):
        pass

    def dict_get(self, dict, objkey, default):
        """

        # 获取字典中的objkey对应的值，适用于字典嵌套

        # dict:字典

        # objkey:目标key
        
        # default:找不到时返回的默认值

        >>> dict_get(dict, objkey, default)
        # # 如
        
        >>> dicttest = {"result": {"code": "110002", "msg": "设备设备序列号或验证码错误"}}

        >>> ret = dict_get(dicttest, 'msg', None)

        >>> print(ret)





        """


        tmp = dict
        for k, v in tmp.items():
            if k == objkey:
                return v
            else:
                if type(v) is types.DictType:
                    ret = self.dict_get(v, objkey, default)
                    if ret is not default:
                        return ret
        return default

    # # 如
    # dicttest = {"result": {"code": "110002", "msg": "设备设备序列号或验证码错误"}}
    # ret = dict_get(dicttest, 'msg', None)
    # print(ret)
