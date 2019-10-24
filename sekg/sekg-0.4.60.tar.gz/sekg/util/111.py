# coding:utf-8
import re


def hump2underline(hunp_str):
    '''
    驼峰形式字符串转成下划线形式
    :param hunp_str: 驼峰形式字符串
    :return: 字母全小写的下划线形式字符串
    '''
    # 匹配正则，匹配小写字母和大写字母的分界位置
    p = re.compile(r'([a-z]|\d)([A-Z])')
    print("@@", hunp_str)
    print("##", p.search(hunp_str).group(0))
    # 这里第二个参数使用了正则分组的后向引用
    sub = re.sub(p, r'\1_\2', hunp_str).lower()
    return sub


def underline2hump(underline_str):
    '''
    下划线形式字符串转成驼峰形式
    :param underline_str: 下划线形式字符串
    :return: 驼峰形式字符串
    '''
    # 这里re.sub()函数第二个替换参数用到了一个匿名回调函数，回调函数的参数x为一个匹配对象，返回值为一个处理后的字符串
    sub = re.sub(r'(_\w)', lambda x: x.group(1)[1].upper(), underline_str)
    return sub


def test_hump2underline():
    # 供测试用的一些驼峰形式的字符串
    attr1 = 'PersonNamePattern'
    attr2 = 'IPv6Address'
    attr3 = 'personDetailInfo'
    attr4 = 'CCTV'
    attr5 = 'CCTVAddress'
    attr6 = 'name'
    attrs = [attr1, attr2, attr3, attr4, attr5, attr6]

    # 遍历attrs进行匹配和转换，把驼峰形式的字符串转成下划线形式
    for attr in attrs:
        sub = hump2underline(attr)
        print(sub)

    # 输出：
    '''
    person_name_pattern
    ipv6_address
    person_detail_info
    cctv
    cctvaddress
    name
    '''
