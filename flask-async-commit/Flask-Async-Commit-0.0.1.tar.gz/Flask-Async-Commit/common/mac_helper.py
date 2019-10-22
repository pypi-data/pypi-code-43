# coding: utf-8


def mac_to_int(mac):
    """
    将mac地址转成十进制int，存入数据库前需要执行这一步
    :param mac: str型
    :return:int型整数
    """
    return int(mac, 16)


def int_to_mac(h):
    """
    将int数转为mac地址（16进制），在取出数据后做这一步
    :param h: int型整数
    :return: 去掉0x前缀，所有字母大写的str
    """
    return str(hex(h)).replace('0x', '').upper()


if __name__ == '__main__':
    print('1.\t', mac_to_int('ac123'))
    print('2.\t', int_to_mac(704803))
    print('3.\t', mac_to_int('AC123'))
    print('3.\t', mac_to_int('0xAC123'))
