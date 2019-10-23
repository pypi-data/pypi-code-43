"""
中文字符编码： u4e00 - u9fa5
英文字符编码: 使用ord来判断ascii, a-z: 97-122 A-Z: 65-90
数字: isdigit
空格: isspace
"""
__all__ = ['is_chinese_char', 'is_english_char', 'check_lang']

def is_chinese_char(ch):
    if '\u4e00' <= ch <= '\u9fa5':
        return True
    return False

def is_english_char(ch):
    if 65 <= ord(ch) <= 90 or 97 <= ord(ch) <= 122:
        return True
    return False

def check_lang(text):
    """ 判断语言类型: en, cn
    """
    en_count = 0
    cn_count = 0
    count = 0
    for _char in text:
        if is_chinese_char(_char):
            cn_count += 1
        elif is_english_char(_char):
            en_count += 1
        count += 1
    
    if en_count/ count >= 0.6:
        return 'en'
    elif cn_count/count >= 0.6:
        return 'cn'
    else:
        return 'unknown'