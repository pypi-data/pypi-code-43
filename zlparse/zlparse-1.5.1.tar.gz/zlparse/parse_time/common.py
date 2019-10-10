import datetime
import pandas as pd
from bs4 import BeautifulSoup
import re
import time

num_chr_map_dict = {'О': '0', 'O': '0', '-': '-', '〇': '0', '0': '0', '零': 0,
                    '一': 1, '二': 2, '两': 2, '三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9, '十': 10,
                    '1': 1, '2': 2, '3': 3, '4': 4, '5': 5, '6': 6, '7': 7, '8': 8, '9': 9,
                    '年': '年', '月': '月', '日': '日'}


def chinese2digits(uchars_chinese):
    uchars = re.findall('(.{4}年.{,4}月.{,4}日)', uchars_chinese)
    total = ''
    if uchars != []:
        uchars = uchars[-1]
        for i in uchars:
            val = num_chr_map_dict.get(i, None)
            if val:
                total += str(val)
        try:
            month, day = re.findall('(\d+)月(\d+)日', total)[0]
        except:
            return None
        if len(month) > 2:
            if '0' in month:
                month = month.replace('0', '')
        if len(day) > 2:
            if len(day) == 3:
                if not day.endswith('0'):
                    day = day.replace('0', '')
                else:
                    day = day[0] + day[-1]
            elif len(day) == 4:
                day = day.replace('10', '')
        total = re.sub('(?<=月)(\d+)', day, total)
        total = re.sub('(\d+)(?=月)', month, total)
        return total
    return uchars_chinese

def ext_from_ggtime(ggstart_time):
    t1 = ggstart_time
    a = re.findall('([1-9][0-9]{3})[\-\./\\年]([0-9]{1,2})[\-\./\\月]([0-9]{1,2}) ([0-9]{2}):([0-9]{2}):([0-9]{2})', t1)

    if a != []:
        y = a[0]
        x = y[0] + "-" + (y[1] if len(y[1]) == 2 else '0%s' % y[1]) + '-' + (y[2] if len(y[2]) == 2 else '0%s' % y[2])
        return x

    a = re.findall('([1-9][0-9]{3})[\-\./\\年]([0-9]{1,2})[\-\./\\月]([0-9]{1,2})', t1)
    if a != []:
        y = a[0]
        x = y[0] + "-" + (y[1] if len(y[1]) == 2 else '0%s' % y[1]) + '-' + (y[2] if len(y[2]) == 2 else '0%s' % y[2])
        return x

    a = re.findall('^([0-2][0-9])[\-\./\\年]([0-9]{1,2})[\-\./\\月]([0-9]{1,2})', t1)
    if a != []:
        y = a[0]
        x = y[0] + "-" + (y[1] if len(y[1]) == 2 else '0%s' % y[1]) + '-' + (y[2] if len(y[2]) == 2 else '0%s' % y[2])
        x = '20' + x
        return x

    a = re.findall('^(20[0-9]{2})--([0-9]{1,2})-([0-9]{1,2})', t1)

    if a != []:
        x = '-'.join([a[0][0], a[0][1] if a[0][1] != '0' else '1', a[0][2] if a[0][2] != '0' else '1'])

        return x

    if ' CST ' in t1:
        try:
            x = time.strptime(t1, '%a %b %d %H:%M:%S CST %Y')
            x = time.strftime('%Y-%m-%d %H:%M:%S', x)
        except:
            x = ''
        if x != '': return x
    a = re.findall('^(20[0-9]{6})', t1)
    if a != []:
        x = '-'.join([a[0][:4], a[0][4:6], a[0][6:8]])
        return x

    return None


def extime_fbsj(ggstart_time, page):
    soup = BeautifulSoup(page, 'lxml')
    txt = re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/]', '', soup.text.strip())
    p = "(?:发布时间|信息时间|录入时间|发稿时间)[：:](20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})"
    a = re.findall(p, txt.replace('documentwrite', ''))
    if a != []:
        return '-'.join(a[0])
    return None


def extime(ggstart_time, page):
    soup = BeautifulSoup(page, 'lxml')
    txt = re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/\.]', '', soup.text.strip())
    p = "(?:更新日期|变更日期|更新时间|发文日期|发表时间|公示日期|发布于|公告时间|公示时间|发布日期)[：:](20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})"
    a = re.findall(p, txt.replace('documentwrite', ''))
    if a != []:
        return '-'.join(a[0])
    return None


def extime_xxsj(ggstart_time, page):
    soup = BeautifulSoup(page, 'lxml')
    txt = re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/]', '', soup.text.strip())
    p = "(?:信息时间)[：:](20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})"
    a = re.findall(p, txt.replace('documentwrite', ''))
    if a != []:
        return '-'.join(a[0])
    return None


def extime_guangdong_guangdongsheng_zfcg(ggstart_time, page):
    list1 = []
    soup = BeautifulSoup(page, 'lxml')
    soup_input = soup.find_all('input')[-3:]
    for i in soup_input:
        value = i['value']
        list1.append(value)
    if list1 != []:
        return ('-'.join([list1[0], list1[1], list1[2]]))
    return None


def extime_transfrom_yunan(ggstart_time, page):
    soup = BeautifulSoup(page, 'lxml')
    txt = re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/]', '', soup.text.strip())
    p = '(?:发布时间|提交时间|公示时间)[：:]{0,1}(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})'

    a = re.findall(p, txt)
    if a != []:
        return ('-'.join(a[0]))
    return None


def strptime_transfrom_yue_r_n(ggstart_time, page):
    soup = BeautifulSoup(page, 'lxml')
    txt = re.sub('^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/', '', soup.text.strip())
    p = "(?:信息时间|信息日期|信息发布日期|发稿时间|发布时间|生成日期)[：:]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})[\-\.\\日/](20[0-2][0-9])"
    a = re.findall(p, txt)
    if a != []:
        return (a[0][2] + '-' + a[0][0] + '-' + a[0][1])
    return None


def extime_xxsj_v2(ggstart_time, page):
    res = extime_xxsj(ggstart_time, page)
    if not res:
        return res
    else:
        return ggstart_time


def extime_fbsj_v2(ggstart_time, page):
    # if ggstart_time is not None:
    #     res = ggstart_time
    # else:
    #     res = extime_fbsj(ggstart_time, page)
    res = extime_fbsj(ggstart_time, page)
    if not res:
        return res
    else:
        return ggstart_time


def extime_v2(ggstart_time, page):
    res = extime(ggstart_time, page)
    if not res:
        return res
    else:
        return ggstart_time


def extime_qg_1_zfcg(ggstart_time, page):
    soup = BeautifulSoup(page, 'lxml')
    txt = soup.find_all('div', attrs={'class': 'pages_date'})
    if txt != []:
        txt = soup.find_all('div', attrs={'class': 'pages_date'})[0]
        txt = re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/]', '', txt.text.strip())
        p = '(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})'
        a = re.findall(p, txt.replace('documentwrite', ''))
        if a != []:
            return '-'.join(a[0])
        return None
    return None


def extime_daili_www_xhtc_com_cn(ggstart_time, page):
    soup = BeautifulSoup(page, 'lxml')
    txt = soup.find_all('div', attrs={'class': 'newstime'})
    if txt != []:
        txt_span = soup.find_all('div', attrs={'class': 'newstime'})[0]
        txt = txt_span.find('span')
        txt = re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/]', '', txt.text.strip())
        p = '(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})'
        a = re.findall(p, txt.replace('documentwrite', ''))
        if a != []:
            return '-'.join(a[0])
        return None
    return None


def extime_henan_henansheng_1_daili(ggstart_time, page):
    soup = BeautifulSoup(page, 'lxml')
    txt = soup.find_all('div', attrs={'class': 'infos'})
    if txt != []:
        txt = soup.find_all('div', attrs={'class': 'infos'})[0]
        txt = re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/]', '', txt.text.strip())
        p = '(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})'
        a = re.findall(p, txt.replace('documentwrite', ''))
        if a != []:
            return '-'.join(a[0])
        return None
    return None


def extime_ningxia_ningxiasheng_zfcg_ningxia_yinchuan_zfcg(ggstart_time, page):
    soup = BeautifulSoup(page, 'lxml')
    txt = soup.find_all('span', attrs={'id': 'pubTime'})
    if txt != []:
        txt = soup.find_all('span', attrs={'id': 'pubTime'})[0]
        txt = re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/]', '', txt.text.strip())
        p = '(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})'
        a = re.findall(p, txt.replace('documentwrite', ''))
        if a != []:
            return '-'.join(a[0])
        return None
    return None


def extime_shandong_qingdao_zfcg(ggstart_time, page):
    soup = BeautifulSoup(page, 'lxml')
    txt = soup.find_all('div', attrs={'class': 'biaotq'})
    if txt != []:
        txt = soup.find_all('div', attrs={'class': 'biaotq'})[0]
        txt = re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/]', '', txt.text.strip())
        p = '(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})'
        a = re.findall(p, txt.replace('documentwrite', ''))
        if a != []:
            return '-'.join(a[0])
        return None
    return


def extime_qycg_eps_hnagroup_com(ggstart_time, page):
    soup = BeautifulSoup(page, 'lxml')
    txt = re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/]', '', soup.text.strip())
    p = "(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})发布"
    a = re.findall(p, txt.replace('documentwrite', ''))
    if a != []:
        return '-'.join(a[0])
    return None


def extime_daili_www_cfet_com_cn(ggstart_time, page):
    soup = BeautifulSoup(page, 'lxml')
    txt = soup.find_all('span', attrs={'id': 'pubTime'})
    if txt != []:
        txt = soup.find_all('span', attrs={'id': 'pubTime'})[0]
        txt = re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/]', '', txt.text.strip())
        p = '(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})'
        a = re.findall(p, txt.replace('documentwrite', ''))
        if a != []:
            return '-'.join(a[0])
        return None
    return None


def extime_sichuan_luzhou_ggzy(ggstart_time, page):
    soup = BeautifulSoup(page, 'lxml')
    txt = soup.find_all('p', attrs={'class': 'news-article-info'})
    if txt != []:
        txt_pan = soup.find_all('p', attrs={'class': 'news-article-info'})[0]
        txt = re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/]', '', txt_pan.text.strip())
        p = '(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})'
        a = re.findall(p, txt.replace('documentwrite', ''))
        if a != []:
            return '-'.join(a[0])
    else:
        txt = soup.find_all('div', attrs={'class': 'ewb-results-date'})
        if txt != []:
            txt = soup.find_all('div', attrs={'class': 'ewb-results-date'})[0]
            txt = re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/]', '', txt.text.strip())
            p = '(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})'
            a = re.findall(p, txt.replace('documentwrite', ''))
            if a != []:
                return '-'.join(a[0])
            return None


def extime_liaoning_huludao_ggzy(ggstart_time, page):
    soup = BeautifulSoup(page, 'lxml')
    txt = soup.find_all('td', attrs={'class': 'title_main2'})
    if txt != []:
        txt = soup.find_all('td', attrs={'class': 'title_main2'})[0]
        txt = re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/]', '', txt.text.strip())
        p = '(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})'
        a = re.findall(p, txt.replace('documentwrite', ''))
        if a != []:
            return '-'.join(a[0])
        return None
    else:
        txt = re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/]', '', soup.text.strip())
        p = '信息日期[:：](20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})'
        a = re.findall(p, txt.replace('documentwrite', ''))
        if a != []:
            return '-'.join(a[0])
        return None


def extime_jiangxi_dexing_ggzy1(ggstart_time, page):
    soup = BeautifulSoup(page, 'lxml')
    txt = soup.find_all('div', attrs={'class': 'property'})
    txt1 = soup.find_all('p', attrs={'class': 'infotime'})
    if txt != []:
        txt_span = soup.find_all('div', attrs={'class': 'property'})[0]
        txt = txt_span.find('span')
        txt = re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/]', '', txt.text.strip())
        p = '(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})'
        a = re.findall(p, txt.replace('documentwrite', ''))
        if a != []:
            return '-'.join(a[0])
    elif txt1 != []:
        txt = soup.find_all('p', attrs={'class': 'infotime'})[0]
        txt = re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/]', '', txt.text.strip())
        p = '(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})'
        a = re.findall(p, txt.replace('documentwrite', ''))
        if a != []:
            return '-'.join(a[0])
    else:
        txt = re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/]', '', soup.text.strip())
        p = '发布日期[:：]{0,1}(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})'
        a = re.findall(p, txt.replace('documentwrite', ''))
        if a != []:
            return '-'.join(a[0])
    return None


def extime_guangxi_baise_gcjs(ggstart_time, page):
    soup = BeautifulSoup(page, 'lxml')
    txt = soup.find_all('div', attrs={'class': 'info'})
    if txt != []:
        txt_span = soup.find_all('div', attrs={'class': 'info'})[0]
        txt = txt_span.find_all('span')[0]
        txt = re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/]', '', txt.text.strip())
        p = '(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})'
        a = re.findall(p, txt.replace('documentwrite', ''))
        if a != []:
            return '-'.join(a[0])
        return None
    return None


def extime_tail(ggstart_time, page):
    soup = BeautifulSoup(page, 'lxml')
    tmp = soup.find('style')
    if tmp is not None:
        tmp.clear()
    tmp = soup.find('script')
    if tmp is not None:
        tmp.clear()
    txt = re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/]', '', soup.text.strip())
    p = '(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})'
    a = re.findall(p, txt[-40:])
    if a != []:
        return '-'.join(a[0])
    return None


def extime_shanxi_hanzhong_gcjs(ggstart_time, page):
    soup = BeautifulSoup(page, 'lxml')
    tmp = soup.find('style')
    if tmp is not None:
        tmp.clear()
    tmp = soup.find('script')
    if tmp is not None:
        tmp.clear()
    txt = re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/]', '', soup.text.strip())
    p = '(?:公示日期|公示时间)[:：](20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})'
    a = re.findall(p, txt)
    if a != []:
        return '-'.join(a[0])
    else:
        p = '(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})'
        a = re.findall(p, txt[-40:])
        if a != []:
            return '-'.join(a[-1])
    return None


def extime_shandong_shandongsheng_gcjs(ggstart_time, page):
    soup = BeautifulSoup(page, 'lxml')
    tmp = soup.find('style')
    if tmp is not None:
        tmp.clear()
    tmp = soup.find('script')
    if tmp is not None:
        tmp.clear()
    txt = re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/]', '', soup.text.strip())
    p = '(发布日期[:：]20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})'
    a = re.findall(p, txt)
    if a != []:
        return '-'.join(a[0])
    else:
        p = '(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})'
        a = re.findall(p, txt[-40:])
        if a != []:
            return '-'.join(a[-1])
    return None


def extime_shandong_zoucheng_ggzy(ggstart_time, page):
    soup = BeautifulSoup(page, 'lxml')
    tmp = soup.find('style')
    if tmp is not None:
        tmp.clear()
    tmp = soup.find('script')
    if tmp is not None:
        tmp.clear()
    txt = re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/]', '', soup.text.strip())
    p = '(?:发布时间|公示时间|公示期自)[:：]{0,1}[自]{0,1}(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})'
    a = re.findall(p, txt)
    if a != []:
        return '-'.join(a[0])
    else:
        p = '(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})'
        a = re.findall(p, txt[-40:])
        if a != []:
            return '-'.join(a[0])
    return None


def extime_daili_www_kanti_cn(ggstart_time, page):
    soup = BeautifulSoup(page, 'lxml')
    tmp = soup.find('style')
    if tmp is not None:
        tmp.clear()
    tmp = soup.find('script')
    if tmp is not None:
        tmp.clear()
    txt = re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/]', '', soup.text.strip())
    p = '(?:发布时间|公示时间)[:：](20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})'
    a = re.findall(p, txt)
    if a != []:
        return '-'.join(a[0])
    else:
        p = '(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})'
        a = re.findall(p, txt[-40:])
        if a != []:
            return '-'.join(a[0])
    return None


def extime_qycg_www_zmzb_com(ggstart_time, page):
    soup = BeautifulSoup(page, 'lxml')
    txt = soup.find_all('span', attrs={'id': 'zdsj'})
    if txt != []:
        txt = soup.find_all('span', attrs={'id': 'zdsj'})[0]
        txt = re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/]', '', txt.text.strip())
        p = '(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})'
        a = re.findall(p, txt.replace('documentwrite', ''))
        if a != []:
            return '-'.join(a[0])
        return None
    else:
        txt = re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/]', '', soup.text.strip())
        p = '(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})'
        a = re.findall(p, txt[-40:])
        if a != []:
            return '-'.join(a[0])
    return None


def extime_jiangxi_yingtan_ggzy(ggstart_time, page):
    soup = BeautifulSoup(page, 'lxml')
    tmp = soup.find('style')
    if tmp is not None:
        tmp.clear()
    tmp = soup.find('script')
    if tmp is not None:
        tmp.clear()
    txt = re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/\[\]]', '', soup.text.strip())
    # txt=soup.text
    pattren = ['\[(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})\]',
               '生成日期[:：](20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})',
               '发布日期[:：](20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})',
               ]
    for p in pattren:

        a = re.findall(p, txt)
        if a != []:
            return '-'.join(a[0])
    return None


def extime_shandong_dongying_gcjs(ggstart_time, page):
    soup = BeautifulSoup(page, 'lxml')
    tmp = soup.find('style')
    if tmp is not None:
        tmp.clear()
    tmp = soup.find('script')
    if tmp is not None:
        tmp.clear()
    txt = re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/]', '', soup.text.strip())
    p = '(?:发布日期|公示时间|报名时间)[:：](20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})'
    a = re.findall(p, txt)
    if a != []:
        return '-'.join(a[0])
    else:
        p = '(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})'
        a = re.findall(p, txt[-40:])
        if a != []:
            return '-'.join(a[0])
        return None


def extime_sichuan_suining_ggzy(ggstart_time, page):
    soup = BeautifulSoup(page, 'lxml')
    txt = soup.find_all('p', attrs={'class': 'time1'})
    if txt != []:
        txt = soup.find_all('p', attrs={'class': 'time1'})[0]
        txt = re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/]', '', txt.text.strip())
        p = '(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})'
        a = re.findall(p, txt.replace('documentwrite', ''))
        if a != []:
            return '-'.join(a[0])
    else:
        txt = soup.find_all('p', attrs={'class': 'time'})
        if txt != []:
            txt = soup.find_all('p', attrs={'class': 'time'})[0]
            txt = re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/]', '', txt.text.strip())
            p = '(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})'
            a = re.findall(p, txt.replace('documentwrite', ''))
            if a != []:
                return '-'.join(a[0])
    return None


def extime_xizang_xizangsheng_ggzy(ggstart_time, page):
    soup = BeautifulSoup(page, 'lxml')
    tmp = soup.find('style')
    if tmp is not None:
        tmp.clear()
    tmp = soup.find('script')
    if tmp is not None:
        tmp.clear()
    txt = re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/]', '', soup.text.strip())
    p = '(?:发布时间|公示时间)[:：](20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})'
    a = re.findall(p, txt)
    if a != []:
        return '-'.join(a[0])
    else:
        p = '(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})'
        a = re.findall(p, txt[-40:])
        if a != []:
            return '-'.join(a[0])
        return None


def extime_qycg_b2b_10086_cn(ggstart_time, page):
    soup = BeautifulSoup(page, 'lxml')
    tmp = soup.find('style')
    if tmp is not None:
        tmp.clear()
    tmp = soup.find('script')
    if tmp is not None:
        tmp.clear()
    txt = re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/]', '', soup.text.strip())
    p = '(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})'
    a = re.findall(p, txt[-100:])
    if a != []:
        return '-'.join(a[-1])
    return None


def extime_beijing_beijingshi_gcjs(ggstart_time, page):
    soup = BeautifulSoup(page, 'lxml')
    tmp = soup.find('style')
    if tmp is not None:
        tmp.clear()
    tmp = soup.find('script')
    if tmp is not None:
        tmp.clear()
    txt = re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/]', '', soup.text.strip())
    p = '(?:招标登记日期|发布日期|公示日期[:：])(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})'
    a = re.findall(p, txt)
    if a != []:
        return '-'.join(a[0])
    else:
        p = '日期[:：]{0,1}(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})'
        a = re.findall(p, txt[-200:])
        if a != []:
            return '-'.join(a[-1])
        return None


def extime_gansu_wuwei_ggzy(ggstart_time, page):
    soup = BeautifulSoup(page, 'lxml')
    tmp = soup.find('style')
    if tmp is not None:
        tmp.clear()
    tmp = soup.find('script')
    if tmp is not None:
        tmp.clear()
    txt = re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/]', '', soup.text.strip())
    p = '(?:竞价(公告)开始时间)(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})'
    a = re.findall(p, txt)
    if a != []:
        return '-'.join(a[0])
    else:
        return ggstart_time


def extime_guangxi_qinzhou_zfcg(ggstart_time, page):
    soup = BeautifulSoup(page, 'lxml')
    txt = soup.find_all('ul', attrs={'class': 'xvd'})
    if txt != []:
        txt = soup.find_all('ul', attrs={'class': 'xvd'})[0]
        txt = re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/]', '', txt.text.strip())
        p = '(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})'
        a = re.findall(p, txt.replace('documentwrite', ''))
        if a != []:
            return '-'.join(a[0])
    return None


def extime_heilongjiang_daqing_ggzy(ggstart_time, page):
    soup = BeautifulSoup(page, 'lxml')
    tmp = soup.find('style')
    if tmp is not None:
        tmp.clear()
    tmp = soup.find('script')
    if tmp is not None:
        tmp.clear()
    txt = re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/]', '', soup.text.strip())
    p = '(?:发布时间|开标日期)[:：]{0,1}(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})'
    a = re.findall(p, txt)
    if a != []:
        return '-'.join(a[0])
    else:
        txt = re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/]', '', soup.text.strip())
        p = '(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})'
        a = re.findall(p, txt[-40:])
        if a != []:
            return '-'.join(a[0])
        return ggstart_time


def extime_henan_henansheng_gcjs(ggstart_time, page):
    soup = BeautifulSoup(page, 'lxml')
    txt = re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/]', '', soup.text.strip())
    p = '日期[:：](20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})'
    a = re.findall(p, txt)
    if a != []:
        return '-'.join(a[0])
    return None


def extime_hubei_macheng_ggzy(ggstart_time, page):
    soup = BeautifulSoup(page, 'lxml')
    txt = soup.find_all('li', attrs={'class': 'list-group-item'})
    if txt != []:
        txt = soup.find_all('li', attrs={'class': 'list-group-item'})[0]
        txt = re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/]', '', txt.text.strip())
        p = '(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})'
        a = re.findall(p, txt.replace('documentwrite', ''))
        if a != []:
            return '-'.join(a[0])
    else:
        txt = re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/]', '', soup.text.strip())
        p = '(?:公示时间|公告发布时间)[:：]{0,1}(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})'
        a = re.findall(p, txt)
        if a != []:
            return '-'.join(a[0])
    return ggstart_time


def extime_jiangsu_jiangsusheng_gcjs(ggstart_time, page):
    soup = BeautifulSoup(page, 'lxml')
    tmp = soup.find('style')
    if tmp is not None:
        tmp.clear()
    tmp = soup.find('script')
    if tmp is not None:
        tmp.clear()
    txt = re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/\[\]]', '', soup.text.strip())
    pattren = [
        '公示期自[:：]{0,1}(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.月\\/]([0-9]{,2})',
        '公示开始时间[:：]{0,1}(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.月\\/]([0-9]{,2})',
        '公示起[始止]时间[:：]{0,1}(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.月\\/]([0-9]{,2})',
        '发布日期为(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.月\\/]([0-9]{,2})']
    for p in pattren:
        a = re.findall(p, txt)
        if a != []:
            return '-'.join(a[0])
    return ggstart_time


def extime_liaoning_haicheng_ggzy(ggstart_time, page):
    soup = BeautifulSoup(page, 'lxml')
    txt = re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/]', '', soup.text.strip())
    p = '公告期限[:：](20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})'
    a = re.findall(p, txt)
    if a != []:
        return '-'.join(a[0])
    else:
        p = '(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})'
        a = re.findall(p, txt[-100:])
        if a != []:
            return '-'.join(a[-1])
    return ggstart_time


def extime_liaoning_liaoningsheng_ggzy(ggstart_time, page):
    soup = BeautifulSoup(page, 'lxml')
    tmp = soup.find('style')
    if tmp is not None:
        tmp.clear()
    tmp = soup.find('script')
    if tmp is not None:
        tmp.clear()
    txt = re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/]', '', soup.text.strip())
    p = '(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})'
    a = re.findall(p, txt[-100:])
    if a != []:
        return '-'.join(a[0])
    return ggstart_time


def extime_qycg_fwgs_sinograin_com_cn(ggstart_time, page):
    soup = BeautifulSoup(page, 'lxml')
    try:
        txt = soup.find_all('h2')
        txt[0].find('div').clear()
    except:
        txt = []

    if txt != []:
        txt = soup.find_all('h2')[0]

        txt = re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/]', '', txt.text.strip())
        p = '(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})'
        a = re.findall(p, txt.replace('documentwrite', ''))
        if a != []:
            return '-'.join(a[0])
    return None


def extime_guangxi_guangxisheng_gcjs(ggstart_time, page):
    soup = BeautifulSoup(page, 'lxml')
    tmp = soup.find('style')
    if tmp is not None:
        tmp.clear()
    tmp = soup.find('script')
    if tmp is not None:
        tmp.clear()
    txt = re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/]', '', soup.text.strip())
    p = '(?:公告日期|公示开始时间)[:：]{0,1}(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})'
    a1 = re.findall(p, txt)
    txt = re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/]', '', soup.text.strip())
    p = '(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})'
    a2 = re.findall(p, txt[-40:])
    if a1 != []:
        return '-'.join(a1[0])
    elif a2 != []:
        return '-'.join(a2[0])
    else:
        txt = soup.text
        txt = txt.replace('\n', '')
        p = '(?:报名开始时间)[:：]{0,1}(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})'
        a = re.findall(p, txt)
        if a != []:
            return '-'.join(a[0])
    return ggstart_time


def extime_liaoning_tieling_ggzy(ggstart_time, page):
    soup = BeautifulSoup(page, 'lxml')
    txt = re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/]', '', soup.text.strip())
    p = "(?:公告发布时间|发布时间[:：])(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})"
    a = re.findall(p, txt.replace('documentwrite', ''))
    if a != []:
        return '-'.join(a[0])


def extime_liaoning_liaoningsheng_zfcg(ggstart_time, page):
    soup = BeautifulSoup(page, 'lxml')
    p = '(?:公告期限|录入时间|领取谈判文件时间、地点|报名时间)[:：]{0,1}(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})'
    txt = re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/\、]', '', soup.text.strip())
    a = re.findall(p, txt)
    if a != []:
        return '-'.join(a[0])
    return ggstart_time


def extime_sichuan_sichuansheng_daili(ggstart_time, page):
    soup = BeautifulSoup(page, 'lxml')
    txt = soup.find_all('div', attrs={'class': 'xq_tie'})
    if txt != []:
        txt = soup.find_all('div', attrs={'class': 'xq_tie'})[0]
        txt = re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/]', '', txt.text.strip())
        p = '(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})'
        a = re.findall(p, txt.replace('documentwrite', ''))
        if a != []:
            return '-'.join(a[0])
    return None


def extime_sichuan_mianzhu_zfcg(ggstart_time, page):
    soup = BeautifulSoup(page, 'lxml')
    txt = soup.find_all('div', attrs={'class': 'ht_date'})
    if txt != []:
        txt = soup.find_all('div', attrs={'class': 'ht_date'})[0]
        txt = re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/]', '', txt.text.strip())
        p = '(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})'
        a = re.findall(p, txt.replace('documentwrite', ''))
        if a != []:
            return '-'.join(a[0])
    #     return None
    else:
        txt = re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/]', '', soup.text.strip())
        p = '(?:发布)[:：](20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})'
        a = re.findall(p, txt)
        if a != []:
            return '-'.join(a[0])
    return None


def extime_sichuan_huaying_ggzy(ggstart_time, page):
    soup = BeautifulSoup(page, 'lxml')
    txt = soup.find_all('publishtime')
    if txt != []:
        txt = soup.find_all('publishtime')[0]
        txt = re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/]', '', txt.text.strip())
        p = '(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})'
        a = re.findall(p, txt.replace('documentwrite', ''))
        if a != []:
            return '-'.join(a[0])
        return None
    else:
        txt = re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/]', '', soup.text.strip())
        p = '(?:更新时间|发布时间)[:：](20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})'
        a = re.findall(p, txt)
        if a != []:
            return '-'.join(a[0])
    return None


def extime_sichuan_chengdu_edu(ggstart_time, page):
    soup = BeautifulSoup(page, 'lxml')
    txt = soup.find_all('span', attrs={'class': 'time'})
    if txt != []:
        txt = soup.find_all('span', attrs={'class': 'time'})[0]
        txt = txt.text
        p = '(20[0-2][0-9])[\-\.年\\/]{2}([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]{2}([0-9]{,2})'
        a = re.findall(p, txt)
        if a != []:
            return '-'.join(a[0])
    return None


def extime_jilin_changchun_edu(ggstart_time, page):
    soup = BeautifulSoup(page, 'lxml')
    txt = soup.find_all('div', string=re.compile('来源'))
    if txt != []:
        txt = soup.find_all('div', string=re.compile('来源'))[0]
        txt = txt.text
        # txt = re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/]', '', txt.text.strip())
        p = '(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,3})'
        a = re.findall(p, txt)
        if a != []:
            return '-'.join(a[0])
    return None


def extime_jiangsu_changzhou_edu(ggstart_time, page):
    soup = BeautifulSoup(page, 'lxml')
    txt = re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/]', '', soup.text.strip())
    pattren = [
        '发布日期[:：](20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})',
        '发表时间[:：](20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})',
        '发布时间[:：](20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})',
    ]
    for p in pattren:
        a = re.findall(p, txt)
        if a != []:
            return '-'.join(a[0])
    return None


def extime_hubei_shennongjia_ggzy(ggstart_time, page):
    soup = BeautifulSoup(page, 'lxml')
    p = '(?:公示期为)(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})'
    txt = re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/\.]', '', soup.text.strip())
    a = re.findall(p, txt)
    if a != []:
        return '-'.join(a[0])
    else:
        txt = re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/\.]', '', soup.text.strip())
        p = '(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})'
        a = re.findall(p, txt[-1000:])
        if a != []:
            return '-'.join(a[-1])
    return ggstart_time


def extime_heilongjiang_heihe_wudalianchi_ggzy(ggstart_time, page):
    soup = BeautifulSoup(page, 'lxml')
    txt = re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/]', '', soup.text.strip())
    pattren = [
        '更新时间[:：](20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})',
        '公告发布日期[:：](20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})',
        '公示起止日期[:：](20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})'
    ]
    for p in pattren:
        a = re.findall(p, txt)
        if a != []:
            return '-'.join(a[0])
    return None


def extime_daili_www_cobo91_com(ggstart_time, page):
    soup = BeautifulSoup(page, 'lxml')
    txt = soup.text.replace('\n', '')
    txt = soup.text.replace(' ', '')
    txt = txt[-200:]
    try:
        txt = chinese2digits(txt)
        p = "(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})"
        a = re.findall(p, txt)
        if a != []:
            return '-'.join(a[-1])
    except:
        return ggstart_time


def extime_chongqing_shapingba_zfcg(ggstart_time, page):
    soup = BeautifulSoup(page, 'lxml')
    txt = soup.find_all('div', attrs={'class': 'news_conent_two_js'})
    if txt != []:
        txt = soup.find_all('div', attrs={'class': 'news_conent_two_js'})[0]
        # txt=txt.text
        txt = re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/]', '', txt.text.strip())
        p = '(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,3})'
        a = re.findall(p, txt)
        if a != []:
            return '-'.join(a[0])
        else:

            return ggstart_time
    return ggstart_time


def extime_daili_www_baili21_com(ggstart_time, page):
    soup = BeautifulSoup(page, 'lxml')
    txt = re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/]', '', soup.text.strip())
    p = "(?:发布于)[：:](20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})"
    a = re.findall(p, txt)
    if a != []:
        return '-'.join(a[0])
    return None


def extime_yunnan_yunnansheng_8_daili(ggstart_time, page):
    soup = BeautifulSoup(page, 'lxml')
    txt = re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/]', '', soup.text.strip())
    p = '发布时间[:：]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})'
    a = re.findall(p, txt)
    if a != []:
        a = '-'.join(a[0])
        p = '(20[0-2][0-9])[\-\.年\\/]'
        if re.findall(p, txt) != []:
            b = re.findall(p, txt)[0]
            c = b + '-' + a
            return c
    return None


def extime_hebei_hebeisheng_daili(ggstart_time, page):
    soup = BeautifulSoup(page, 'lxml')
    txt = re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/]', '', soup.text.strip())
    pattren = ['发布人[:：][\u4E00-\u9Fa50-9]{0,20}(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})',
               '公告期限[\u4E00-\u9Fa50-9]{0,20}自(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})',
               '公示时间从(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})',
               '定标日期[:：](20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})',
               '发布时间[:：](20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})',
               '发布日期[:：](20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})',
               '公司(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})',
               '请于(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})',
               ]
    for p in pattren:
        a = re.findall(p, txt)
        if a != []:
            return '-'.join(a[0])
    return ggstart_time


def extime_guangdong_shenzhen_6_daili(ggstart_time, page):
    soup = BeautifulSoup(page, 'lxml')
    txt = soup.text
    p = '(?:添加时间)[:：](20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,3})'
    a = re.findall(p, txt)
    if a != []:
        if len(a[0][-1]) > 2:
            return a[0][0] + "-" + a[0][1] + "-" + a[0][2][-2:]
        return '-'.join(a[0])
    return None


def extime_guangdong_guangdongsheng_19_daili(ggstart_time, page):
    soup = BeautifulSoup(page, 'lxml')
    txt = re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/]', '', soup.text.strip())
    p = '(?:公示日期|发布招标公告时间|报名时间)[:：](20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,3})'
    a = re.findall(p, txt)
    if a != []:
        return '-'.join(a[0])
    return None


def extime_guangdong_guangdongsheng_21_daili(ggstart_time, page):
    soup = BeautifulSoup(page, 'lxml')
    txt = re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/]', '', soup.text.strip())
    p = '(?:公示时间|公告发布开始时间)[:：](20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,3})'
    a = re.findall(p, txt)
    if a != []:
        return '-'.join(a[0])
    return None


def extime_guangdong_guangdongsheng_22_daili(ggstart_time, page):
    soup = BeautifulSoup(page, 'lxml')
    tmp = soup.find('style')
    if tmp is not None:
        tmp.clear()
    tmp = soup.find('script')
    if tmp is not None:
        tmp.clear()
    txt = re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/\[\]]', '', soup.text.strip())
    p = '(?:开标日期[:：]{0,1}|公告期限自|公示期为{0,1}[:：]{0,1}|公示时间从|公示期间为自|本公告期限[0-9]个工作日[:：]{0,1}自|公告日期[:：]{0,1}为{0,1})(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})'
    a = re.findall(p, txt)
    if a != []:
        return '-'.join(a[0])
    else:
        try:
            txt = soup.text.replace('\n', '')
            txt = soup.text.replace(' ', '')
            txt = txt[-200:]
            txt = chinese2digits(txt)
            p = '(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,3})'
            a = re.findall(p, txt)
            if a != []:
                return '-'.join(a[0])
        except:
            return ggstart_time
    return ggstart_time


def extime_guangdong_guangdongsheng_24_daili(ggstart_time, page):
    soup = BeautifulSoup(page, 'lxml')
    tmp = soup.find('style')
    if tmp is not None:
        tmp.clear()
    tmp = soup.find('script')
    if tmp is not None:
        tmp.clear()
    txt = re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/\[\]]', '', soup.text.strip())
    p = '(?:发布时间[:：]|公告期限自|公示期为)(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})'
    a = re.findall(p, txt)
    if a != []:
        return '-'.join(a[0])
    else:
        p = '(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})'
        a = re.findall(p, txt[-40:])
        if a != []:
            return '-'.join(a[0])
    return None


def extime_jiangxi_jiangxisheng_2_daili(ggstart_time, page):
    soup = BeautifulSoup(page, 'lxml')
    txt = re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/]', '', soup.text.strip())
    p = '(?:定标日期[:：]|招标活动于)(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,3})'
    a = re.findall(p, txt)
    if a != []:
        return '-'.join(a[0])
    else:
        p = '(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})'
        a = re.findall(p, txt[-200:])
        if a != []:
            return '-'.join(a[0])
    return None


def extime_shandong_shandongsheng_4_daili(ggstart_time, page):
    soup = BeautifulSoup(page, 'lxml')
    txt = soup.find_all('div', attrs={'class': 'nrrbbnr'})
    try:
        if txt != []:
            txt = soup.find_all('div', attrs={'class': 'nrrbbnr'})[0]
            txt = soup.text.replace('\n', '')
            txt = soup.text.replace(' ', '')
            txt = txt[-40:]
            txt = chinese2digits(txt)
            p = '(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,3})'
            a = re.findall(p, txt)
            if a != []:
                return '-'.join(a[0])
    except:
        return None


def extime_tail1(ggstart_time, page):
    soup = BeautifulSoup(page, 'lxml')
    tmp = soup.find('style')
    if tmp is not None:
        tmp.clear()
    tmp = soup.find('script')
    if tmp is not None:
        tmp.clear()
    txt = re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/\.]', '', soup.text.strip())
    p = '(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})'
    a = re.findall(p, txt[-100:])
    if a != []:
        return '-'.join(a[-1])
    return ggstart_time


def extime_daili_www_zhengdapengan_com(ggstart_time, page):
    soup = BeautifulSoup(page, 'lxml')
    txt = soup.find_all('div', attrs={'class': 'hits'})
    if txt != []:
        txt = soup.find_all('div', attrs={'class': 'hits'})[0]
        txt = re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/]', '', txt.text.strip())
        p = '(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})'
        a = re.findall(p, txt.replace('documentwrite', ''))
        if a != []:
            return '-'.join(a[0])
        return None
    else:
        txt = re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/]', '', soup.text.strip())
        p = '(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})'
        a = re.findall(p, txt[-200:])
        if a != []:
            return '-'.join(a[-1])
    return None
def extime_daili_www_zjtaiyu_cn(ggstart_time, page):
    soup = BeautifulSoup(page, 'lxml')
    txt=soup.find_all('span',attrs={'class':'date'})
    if txt!=[]:
        txt=soup.find_all('span',attrs={'class':'date'})[0]
        txt = re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/\.]', '', txt.text.strip())
        p='(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})'
        a = re.findall(p, txt)
        if a != []:
            return '-'.join(a[0])
    return None

def extime_yunnan_yunnansheng_24_daili(ggstart_time, page):
    soup = BeautifulSoup(page, 'lxml')
    txt=soup.find_all('li',attrs={'class':'entry-date'})
    if txt!=[]:
        txt=soup.find_all('li',attrs={'class':'entry-date'})[0]  
        p='(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})'
        a = re.findall(p, txt.text.strip())

        if a != []:
            return '-'.join(a[0])

def extime_tianjin_tianjinshi_1_edu(ggstart_time, page):
    soup = BeautifulSoup(page, 'lxml')
    txt=soup.find_all('div',attrs={'class':'newstime'})
    try:
        if txt!=[]:
            txt=soup.find_all('div',attrs={'class':'newstime'})[0]  
            p='(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,3})'
            a = re.findall(p, txt.text.strip())
            if a != []:
                return '-'.join(a[0])
    except:
        return None

def extime_sichuan_sichuansheng_7_daili(ggstart_time, page):
    soup = BeautifulSoup(page, 'lxml')
    txt = re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/]', '', soup.text.strip())
    pattren=[                   
      '公告发布时间[:：]{0,1}(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})',  
      '自(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})', 
      '文件时间[:：]{0,1}(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})',    
      '开始时间{0,1}(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})',     
      '通知书时间[:：](20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})',      
      '请于(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})',        
     ]
    for p in pattren:
        a = re.findall(p, txt)
        if a != []:
            return '-'.join(a[0])
    a = re.findall(p, txt)
    if a != []:
        return '-'.join(a[0])
    else:    
        p='(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})'
        a = re.findall(p,txt[-200:])
        if a != []:
            return '-'.join(a[-1])                     
    return ggstart_time

def extime_sichuan_chengdu_3_edu(ggstart_time, page):
    soup = BeautifulSoup(page, 'lxml')
    txt = re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/]', '', soup.text.strip())
    pattren=[                  
      '公告发布时间(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})',  
     ]
    for p in pattren:
        a = re.findall(p, txt)
        if a != []:
            return '-'.join(a[0])
    a = re.findall(p, txt)
    if a != []:
        return '-'.join(a[0])
    else:    
        p='(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})'
        a = re.findall(p,txt[-200:])
        if a != []:
            return '-'.join(a[-1])                     
    return ggstart_time

def extime_heilongjiang_heilongjiangsheng_3_daili(ggstart_time,page):
    soup = BeautifulSoup(page, 'lxml')
    txt = re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/]', '', soup.text.strip())
    pattren=[
      '流标公告发布日期[:：](20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})',
       '公示日期[:：](20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})',
      '发布时间[:：](20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})',
      '招标公告日期[:：](20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})',
      '公告时间[:：](20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})',
      '请{0,1}于(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})',
      '下载时间为(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})',
      '公示起止日期[:：](20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})',
       '开标时间[:：](20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})',
     ]
    for p in pattren:
        a = re.findall(p, txt)
        if a != []:
            return '-'.join(a[0])
    if a != []:
        return '-'.join(a[0])
    else:
        p='(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})'
        a = re.findall(p,txt[-200:])
        if a != []:
            return '-'.join(a[-1])
    return None


def extime_hebei_zhangjiakou_zfcg(ggstart_time, page):
    soup = BeautifulSoup(page, 'lxml')
    txt = re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/]', '', soup.text.strip())
    pattren=[
      '(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})来源',  
     ]
    for p in pattren:
        a = re.findall(p, txt)
        if a != []:
            return '-'.join(a[0])
    return ggstart_time

def extime_hebei_hebeisheng_2_daili(ggstart_time, page):
    soup = BeautifulSoup(page, 'lxml')
    txt = soup.text.strip()
    pattren=[
      '发布时间[:：](20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})',  
     ]
    for p in pattren:
        a = re.findall(p, txt)
        if a != []:
            return '-'.join(a[0])
    return None

def extime_guangdong_shenzhen_20_daili(ggstart_time, page):
    soup = BeautifulSoup(page, 'lxml')
    tmp = soup.find('style')
    if tmp is not None:
        tmp.clear()
    tmp = soup.find('script')
    if tmp is not None:
        tmp.clear()         
    txt=soup.text.replace('\n','')
    txt=soup.text.replace(' ','')
    txt=txt[-200:]
    try:
      txt=chinese2digits(txt)
      p = "(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})"
      a = re.findall(p,txt)
      if a != []:
          return '-'.join(a[-1])   
    except:
        return ggstart_time

def extime_guangdong_huizhou_daili(ggstart_time, page):
    soup = BeautifulSoup(page, 'lxml')
    tmp = soup.find('style')
    if tmp is not None:
        tmp.clear()
    tmp = soup.find('script')    
    txt = re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/]', '', soup.text.strip())
    p='(?:公示开始时间)[：:](20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})'       
    a = re.findall(p, txt) 
    if a != []:
        return '-'.join(a[0])
    else:
        p='(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})'
        a = re.findall(p,txt[-200:])
        if a != []:
            return '-'.join(a[-1])                     
    return ggstart_time

def extime_gansu_lanzhou_edu(ggstart_time, page):
    soup = BeautifulSoup(page, 'lxml')
    txt=soup.text.replace('\n','')
    txt=soup.text.replace(' ','')
    txt=txt[-200:]
    try:
      txt=chinese2digits(txt)
      p = "(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})"
      a = re.findall(p,txt)
      if a != []:
          return '-'.join(a[-1])
      else:
        txt=soup.text.replace('\n','')
        txt=soup.text.replace(' ','')
        p="(?:发布时间)[:：](20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})"
        a = re.findall(p,txt)
        if a != []:
            return '-'.join(a[0])        
    except:
        return None

def extime_chongqing_chongqingshi_2_edu(ggstart_time, page):
    soup = BeautifulSoup(page, 'lxml')
    txt = re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/]', '', soup.text.strip())
    pattren=[
      '发布时间[:：](20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})',  
      '发布日期[:：](20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})',       
     ]
    for p in pattren:
        a = re.findall(p, txt)
        if a != []:

            return '-'.join(a[0])
    return None

def extime_beijing_beijingshi_5_edu(ggstart_time, page):
    soup = BeautifulSoup(page, 'lxml')
    txt = re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/]', '', soup.text.strip())
    p='(?:公示时间)(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})'
    a = re.findall(p, txt)
    if a != []:

        return '-'.join(a[0])
    return ggstart_time

def extime_anhui_anhuisheng_3_daili(page,ggstart_time):
    soup = BeautifulSoup(page, 'lxml')
    txt = re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/]', '', soup.text.strip())
    pattren=[
      '公示期[:：](20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})',
      '公示时间(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})',
      '开标(采购)日期[:：](20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})',
      '报名时间[:：](20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})',
      '谈判文件发售时间[:：](20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})',
      '招标公告发布时间{0,1}(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})',
      '日期[:：](20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})',
     ]
    for p in pattren:
        a = re.findall(p, txt)
        if a != []:
            return '-'.join(a[0])
    else:    
        p='(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})'
        a = re.findall(p,txt[-200:])
        if a != []:
            return '-'.join(a[-1])                     
    return ggstart_time

def extime_qycg_zbpt_zjzttx_com_cn(ggstart_time, page):
    soup = BeautifulSoup(page, 'lxml')
    txt=soup.find_all('div',attrs={'class':'padding5 TxtCenter'})
    if txt!=[]:
        txt=soup.find_all('div',attrs={'class':'padding5 TxtCenter'})[0]
        txt = re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/\.]', '', txt.text.strip())
        p='(20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})'
        a = re.findall(p, txt)
        if a != []:
            return '-'.join(a[0])
    return None


def extime_qycg_bid_sichuanair_com(ggstart_time, page):
    soup = BeautifulSoup(page, 'lxml')
    txt = re.sub('[^\u4E00-\u9Fa5a-zA-Z0-9:：\-\\/\.]', '', soup.text.strip())
    panttren=[
     '发布日期[：:](20[0-2][0-9])[\-\.年\\/]([1-9]|[0][1-9]|[1][0-2])[\-\.\\月/]([0-9]{,2})',
     ]
    for p in panttren:
        a = re.findall(p, txt.replace('documentwrite', ''))
        if a != []:

            return '-'.join(a[-1])
    return None


