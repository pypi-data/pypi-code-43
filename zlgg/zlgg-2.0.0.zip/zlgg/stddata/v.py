
import re 

def extprice(price):
    if price is None:return None 
    CN_NUM = {
        '〇' : 0, '一' : 1, '二' : 2, '三' : 3, '四' : 4, '五' : 5, '六' : 6, '七' : 7, '八' : 8, '九' : 9, '零' : 0,
        '壹' : 1, '贰' : 2, '叁' : 3, '肆' : 4, '伍' : 5, '陆' : 6, '柒' : 7, '捌' : 8, '玖' : 9, '貮' : 2, '两' : 2,
    }

    CN_UNIT = {
        '十' : 10,
        '拾' : 10,
        '百' : 100,
        '佰' : 100,
        '千' : 1000,
        '仟' : 1000,
        '万' : 10000,
        '萬' : 10000,
        '亿' : 100000000,
        '億' : 100000000,
        '兆' : 1000000000000,
    }

    def chinese_to_arabic(cn:str) -> int:
        unit = 0   # current
        ldig = []  # digest
        for cndig in reversed(cn):
            if cndig in CN_UNIT:
                unit = CN_UNIT.get(cndig)
                if unit == 10000 or unit == 100000000:
                    ldig.append(unit)
                    unit = 1
            else:
                dig = CN_NUM.get(cndig)
                if unit:
                    dig *= unit
                    unit = 0
                ldig.append(dig)
        if unit == 10:
            ldig.append(10)
        val, tmp = 0, 0
        for x in reversed(ldig):
            if x == 10000 or x == 100000000:
                val += tmp * x
                tmp = 0
            else:
                tmp += x
        val += tmp
        return val


    a=re.findall('[四〇伍叁零二八三壹六柒貮一捌九五两贰肆玖七陆億兆佰亿万萬十拾仟千百]{3,}',price)
    if a!=[]:
       result=chinese_to_arabic(a[0])

       return result 

    a=re.findall('([1-9][0-9\.]{0,}[0-9]|0\.[0-9]+)[^%]',price)

    if a!=[]:
       result=a[0] 
       if result.count('.')>1: result='.'.join(result.split('.')[:2])
       if '万' in price:
           result=float(result)
           result=result*10000
       if '亿' in price:
           result=float(result)
           result=result*100000000
       return result 
            
    return None 




def extqyname(qyname):
    if qyname is None:return None
    a=re.findall("^[\u4e00-\u9fa5（）\(\)]{6,}公司",qyname.strip())
    if a!=[]:
        return a[0]
    else:
        return None


def extxmjl(name):
    if name is None:return None 
    a=re.findall("^[\u4e00-\u9fa5]*",name.strip())
    if a!=[]:
        return a[0]
    else:
        return name

