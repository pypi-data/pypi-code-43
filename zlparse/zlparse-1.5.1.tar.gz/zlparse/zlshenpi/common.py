from bs4 import BeautifulSoup
import json
import pandas as pd
import math
import re


def ext_tb1(table):
    soup = BeautifulSoup(table, 'html.parser')

    trs = soup.find_all('tr')
    d = {}
    for tr in trs:
        tds = tr.find_all('td')
        for i in range(int(len(tds) / 2)):
            k, v = tds[2 * i].text.strip(), tds[2 * i + 1].text.strip()
            d[k] = v
    return d


def ext_tb2_beijingshi(table):
    soup = BeautifulSoup(table, 'html.parser')
    trs = soup.find_all('tr')
    txtarr = [[td.text.strip() for td in tr.find_all('td')] for tr in trs][1:4]
    d = {}
    for i in txtarr:
        tds = i
        for j in range(math.ceil((len(tds) / 2))):
            k, v = tds[2 * j], tds[2 * j + 1]
            d[k] = v
    return d


def ext_tb2_hebeisheng(table):
    soup = BeautifulSoup(table, 'html.parser')
    trs = soup.find_all('tr')
    txtarr = [[td.text.strip() for td in tr.find_all('td')] for tr in trs][:10]

    d = {}
    for i in txtarr:
        tds = i
        for j in range(math.ceil((len(tds) / 2))):
            k, v = tds[2 * j], tds[2 * j + 1]
            d[k] = v
    return d


def ext_tb2_quanguo(table):
    soup = BeautifulSoup(table, 'html.parser')
    trs = soup.find_all('tr')
    txtarr = [[td.text.strip() for td in tr.find_all('td')] for tr in trs][:10]
    d = {}
    for i in txtarr:
        tds = i
        for j in range(math.ceil((len(tds) / 2))):
            k, v = tds[2 * j], tds[2 * j + 1]
            d[k] = v
    return d


def ext_tb2_jilinsheng(table):
    soup = BeautifulSoup(table, 'html.parser')
    trs = soup.find_all('tr')
    txtarr = [[td.text.strip() for td in tr.find_all('td')] for tr in trs][1:]
    print(txtarr)
    d = {}
    for i in txtarr:
        tds = i
        for j in range(math.ceil((len(tds) / 2))):
            k, v = tds[2 * j], tds[2 * j + 1]
            d[k] = v
    return d


def ext_anhuisheng(page, fabu_time, info=None):
    if page is None or page == '':
        return ''
    fabu_time = str(fabu_time)

    soup = BeautifulSoup(page, 'html.parser')
    if info is not None:
        if 'jieguo' in info:
            jieguo = json.loads(info)['jieguo']
        else:
            jieguo = ''
    else:
        jieguo = ''

    result, d = {}, {}
    d = ext_tb1(str(soup.table))
    if d != {}:
        try:
            result = {
                "xmmc": d['项目名称'],
                "xmdm": d['项目代码'],
                "xmdw": d['项目法人单位'],
                "xmtz": "",
                "xmzt": jieguo,
                "xmdz": "",
                "xmgk": "",
                "fabu_time": fabu_time
            }
        except:
            pass
    return json.dumps(result, ensure_ascii=False)


def ext_beijingshi(page, fabu_time, info=None):
    if page is None or page == '':
        return ''
    fabu_time = str(fabu_time)

    soup = BeautifulSoup(page, 'html.parser')
    if info is not None:
        if 'jieguo' in info:
            jieguo = json.loads(info)['jieguo']
        else:
            jieguo = ''
    else:
        jieguo = ''
    result, d = {}, {}
    d = ext_tb1(str(soup.table))
    if d != {}:
        try:

            result = {

                "xmmc": d['项目名称'],
                "xmdm": d['项目代码'],
                "xmdw": d['申请单位'],
                "xmtz": "",
                "xmzt": jieguo,
                "xmdz": "",
                "xmgk": "",
                "fabu_time": fabu_time

            }
        except:
            d = ext_tb2_beijingshi(str(soup.table))
            result = {

                "xmmc": d['项目名称'],
                "xmdm": d['项目代码'],
                "xmdw": d['项目单位'],
                "xmtz": "",
                "xmzt": jieguo,
                "xmdz": "",
                "xmgk": "",
                "fabu_time": fabu_time

            }

    return json.dumps(result, ensure_ascii=False)


def ext_fujiansheng(page, fabu_time, info=None):
    fabu_time = str(fabu_time)
    soup = BeautifulSoup(page, 'html.parser')
    result, d = {}, {}
    d = ext_tb1(str(soup.find_all('table', attrs={"class": "zhuce_table_style txxx_table_style"})))
    if d != '':
        try:
            d = ext_tb1(str(soup.find_all('table', attrs={"class": "zhuce_table_style txxx_table_style"})[0]))
            span = soup.find_all('span', attrs={"name": 'enterpristName'})
            if len(span) > 0:
                xmdw = span[0].text.strip()
            else:
                xmdw = ""
            tr = soup.find_all('tr', attrs={"class": "itemInfo"})
            if len(tr) > 0:
                xmzt = tr[0].find_all('td')[-2].text.strip()
            else:
                xmzt = ""
            result = {
                "xmmc": d['项目名称'],
                "xmdm": d['项目编码'],
                "xmdw": xmdw,
                "xmtz": d['项目总投资(万元)'] + '万元',
                "xmzt": xmzt,
                "xmdz": d['建设详细地址'],
                "xmgk": d['主要建设内容及规模'],
                "fabu_time": fabu_time,
            }
        except:
            pass

    return json.dumps(result, ensure_ascii=False)


def ext_guangdongsheng(page, fabu_time, info=None):
    if page is None or page == '':
        return ''
    fabu_time = str(fabu_time)
    soup = BeautifulSoup(page, 'html.parser')
    result, d = {}, {}
    d = ext_tb1(str(soup.table))
    if d != '':
        try:
            result = {
                "xmmc": d['项目名称'],
                "xmdm": d['备案项目编号'],
                "xmdw": "",
                "xmtz": d['项目总投资'],
                "xmzt": d['项目当前状态'],
                "xmdz": d['项目所在地'],
                "xmgk": d['项目规模及内容'],
                "fabu_time": fabu_time
            }
        except:
            try:
                xmdm = re.findall('(?:项目代码为|项目统一代码为|项目编码为)[:：]([0-9\-]{10,})', soup.text.strip())[0]
                if re.findall('(?:项目总投资为|项目投资估算总额|总投资|工程投资总{0,1}额为)([0-9\.]{0,}万元)', soup.text.strip()) != []:
                    xmtz = re.findall('(?:项目总投资为|项目投资估算总额|总投资|工程投资总{0,1}额为)([0-9\.]{0,}万元)', soup.text.strip())[0] + '万元'
                else:
                    xmtz = ""
                if re.findall('项目建设地点[为]{0,1}(.*?)。', soup.text.strip()) != []:
                    xmdz = xmdz = re.findall('项目建设地点[为]{0,1}(.*?)。', soup.text.strip())[0]
                else:
                    xmdz = ""
                xmdw = soup.find_all('p')[2].text.strip()[:-1]
                xmmc = soup.find_all('p')[1].text.split('工程')[0]
                result = {
                    "xmmc": xmmc,
                    "xmdm": xmdm,
                    "xmdw": xmdw,
                    "xmtz": xmtz,
                    "xmzt": '批复',
                    "xmdz": xmdz,
                    "xmgk": "",
                    "fabu_time": fabu_time
                }
            except:

                pass

    return json.dumps(result, ensure_ascii=False)


def ext_hebeisheng(page, fabu_time, info=None):
    if page is None or page == '':
        return ''
    page = page.replace('<th ', '<td ').replace('</th>', '</td>').replace('<th>', '<td>')
    fabu_time = str(fabu_time)

    soup = BeautifulSoup(page, 'html.parser')
    if info is not None:
        if 'jieguo' in info:

            jieguo = json.loads(info)['jieguo']

        else:

            jieguo = ''
    else:
        jieguo = ''
    result, d = {}, {}
    tbs = soup.find_all('table')
    if len(tbs) > 2:
        d = ext_tb1(str(tbs[1]))
    if d != '':
        try:
            result = {
                "xmmc": d['项目名称'],
                "xmdm": d['项目代码'],
                "xmdw": d['项目法人单位'],
                "xmtz": "",
                "xmzt": jieguo,
                "xmdz": "",
                "xmgk": "",
                "fabu_time": fabu_time
            }
        except:
            if soup.find_all('table', attrs={"class": "m-table m-table-rds"}) != []:
                soup_table = soup.find_all('table', attrs={"class": "m-table m-table-rds"})[0]
                d = ext_tb2_hebeisheng(str(soup_table))
            else:
                d = ""
            try:
                result = {
                    "xmmc": d['项目名称'],
                    "xmdm": d['项目代码'],
                    "xmdw": "",
                    "xmtz": d['项目总投资(万元)'],
                    "xmzt": jieguo,
                    "xmdz": d['建设地点'],
                    "xmgk": d['建设内容与规模'],
                    "fabu_time": fabu_time
                }
            except:
                pass

    return json.dumps(result, ensure_ascii=False)


def ext_heilongjiangsheng(page, fabu_time, info=None):
    if page is None or page == '':
        return ''
    page = page.replace('<th ', '<td ').replace('</th>', '</td>').replace('<th>', '<td>')

    fabu_time = str(fabu_time)

    soup = BeautifulSoup(page, 'html.parser')
    if info is not None:
        if 'jieguo' in info:

            jieguo = json.loads(info)['jieguo']

        else:

            jieguo = ''
    else:
        jieguo = ''
    result, d = {}, {}
    d = ext_tb1(str(soup.table))
    if d != '':
        try:
            result = {
                "xmmc": d['项目名称'],
                "xmdm": d['项目代码'],
                "xmdw": d['项目法人单位'],
                "xmtz": "",
                "xmzt": jieguo,
                "xmdz": "",
                "xmgk": "",
                "fabu_time": fabu_time
            }
        except:
            pass

    return json.dumps(result, ensure_ascii=False)


def ext_henansheng(page, fabu_time, info=None):
    if page is None or page == '':
        return ''
    fabu_time = str(fabu_time)

    soup = BeautifulSoup(page, 'html.parser')

    if info is not None:
        if 'status' in info:

            jieguo = json.loads(info)['status']

        else:

            jieguo = ''
    else:
        jieguo = ''
    result, d1, d2, d = {}, {}, {}, {}
    tbs = soup.find_all('table')
    if len(tbs) >= 2:
        d1, d2 = ext_tb1(str(tbs[0])), ext_tb1(str(tbs[1]))
    d.update(d1)
    d.update(d2)
    if d != '':
        try:
            if d.get('估算总投资(万元)', 0) == 0:
                xmtz = ''
            else:
                xmtz = d['估算总投资(万元)']
            if d.get('单位名称', 0) == 0:
                xmdw = ''
            else:
                xmdw = d['单位名称']
            result = {
                "xmmc": d['项目名称'],
                "xmdm": d['项目代码'],
                "xmdw": xmdw,
                "xmtz": "",
                "xmzt": jieguo,
                "xmdz": xmtz,
                "xmgk": d['建设规模及内容'],
                "fabu_time": fabu_time
            }
        except:
            pass

    return json.dumps(result, ensure_ascii=False)


def ext_hubeisheng(page, fabu_time, info=None):
    if page is None or page == '':
        return ''

    fabu_time = str(fabu_time)

    soup = BeautifulSoup(page, 'html.parser')
    if info is not None:
        if 'result' in info:
            jieguo = json.loads(info)['result']
            print('jieguo', jieguo)
        elif 'shenhe_status' in info:
            jieguo = json.loads(info)['shenhe_status']
        else:
            jieguo = ''
    else:
        jieguo = ''
    result, d = {}, {}
    d = ext_tb1(str(soup.table))
    if d != '':
        try:
            result = {
                'xmmc': d['项目名称：'],
                'xmdm': d['项目代码：'],
                'xmdw': d['单位名称：'],
                'xmtz': d['项目总投资（万元）：'] + '万元',
                'xmzt': jieguo,
                'xmdz': d['建设地点：'],
                'xmgk': d['主要建设规模及内容：'],
                'fabu_time': fabu_time
            }
        except:
            pass
    return json.dumps(result, ensure_ascii=False)


def ext_qinghaisheng(page, fabu_time, info=None):
    if page is None or page == '': return ''

    fabu_time = str(fabu_time)

    soup = BeautifulSoup(page, 'html.parser')
    if info is not None:
        if 'shenpijieguo' in info:
            jieguo = json.loads(info)['shenpijieguo']
        else:
            jieguo = ''
    else:
        jieguo = ''
    result, d = {}, {}

    d = ext_tb1(str(soup.table))
    if d != '':
        try:
            result = {
                "xmmc": d['项目名称'],
                "xmdm": d['项目代码'],
                "xmdw": d['项目法人单位'],
                "xmtz": "",
                "xmzt": jieguo,
                "xmdz": "",
                "xmgk": "",
                "fabu_time": fabu_time
            }
        except:
            pass
    return json.dumps(result, ensure_ascii=False)


def ext_shanxisheng(page, fabu_time, info=None):
    if page is None or page == '':
        return ''
    fabu_time = str(fabu_time)
    soup = BeautifulSoup(page, 'html.parser')
    result, d = {}, {}
    d = ext_tb1(str(soup.table))
    if d != '':
        try:
            result = {
                'xmmc': d['项目名称：'],
                'xmdm': d['项目代码：'],
                'xmdw': d['单位名称：'],
                'xmtz': d['项目总投资（万元）：'] + '(万元)',
                'xmzt': d['审核状态：'],
                'xmdz': d['建设地点：'],
                'xmgk': d['主要建设规模及内容：'],
                'fabu_time': fabu_time
            }
        except:
            pass
    return json.dumps(result, ensure_ascii=False)


def ext_sichuansheng(page, fabu_time, info=None):
    if page is None or page == '':
        return ''
    page = page.replace('<th ', '<td ').replace('</th>', '</td>').replace('<th>', '<td>')

    fabu_time = str(fabu_time)
    if info is not None:
        if 'result' in info:
            jieguo = json.loads(info)['result']
        else:
            jieguo = ''
    else:
        jieguo = ''
    soup = BeautifulSoup(page, 'html.parser')
    result, d = {}, {}
    d = ext_tb1(str(soup.table))
    if d != '':
        try:
            result = {
                "xmmc": d['项目名称'],
                "xmdm": d['项目代码'],
                "xmdw": d['项目单位'],
                "xmtz": d['项目总投资及资金来源'],
                "xmzt": jieguo,
                "xmdz": d['建设地点详情'],
                "xmgk": d['主要建设内容及规模'],
                "fabu_time": fabu_time
            }
        except:
            try:
                result = {
                    "xmmc": d['项目名称'],
                    "xmdm": d['项目代码'],
                    "xmdw": d['项目单位'],
                    "xmtz": "",
                    "xmzt": jieguo,
                    "xmdz": "",
                    "xmgk": "",
                    "fabu_time": fabu_time
                }
            except:
                pass
    return json.dumps(result, ensure_ascii=False)


def ext_xiamenshi(page, fabu_time, info=None):
    if page is None or page == '':
        return ''
    fabu_time = str(fabu_time)
    if 'shenpijieguo' in info:
        jieguo = json.loads(info)['shenpijieguo']
    else:
        jieguo = ''

    soup = BeautifulSoup(page, 'html.parser')

    result, d = {}, {}
    d = ext_tb1(str(soup.table))
    if d != '':
        try:
            result = {
                "xmmc": d['项目名称'],
                "xmdm": d['中央代码/地方代码'],
                "xmdw": d['项目（法人）单位'],
                "xmtz": "",
                "xmzt": jieguo,
                "xmdz": "",
                "xmgk": "",
                "fabu_time": fabu_time
            }
        except:
            pass

    return json.dumps(result, ensure_ascii=False)


def ext_yunnansheng(page, fabu_time, info=None):
    if page is None or page == '':
        return ''
    fabu_time = str(fabu_time)
    soup = BeautifulSoup(page, 'html.parser')
    result, d, d1, d2 = {}, {}, {}, {}
    tbs = soup.find_all('table')
    if len(tbs) >= 2:
        d1 = ext_tb1(str(tbs[0]))
        d2 = ext_tb1(str(tbs[1]))
        d.update(d1)
        d.update(d2)
    if d != '':
        try:
            result = {
                "xmmc": d['项目名称'],
                "xmdm": d['项目代码'],
                "xmdw": "",
                "xmtz": "",
                "xmzt": d["项目状态"],
                "xmdz": d["建设地点"],
                "xmgk": "",
                "fabu_time": fabu_time
            }
        except:
            pass
    return json.dumps(result, ensure_ascii=False)


def ext_quanguo(page, fabu_time, info=None):
    if page is None or page == '':
        return ''
    fabu_time = str(fabu_time)
    soup = BeautifulSoup(page, 'html.parser')
    result, d = {}, {}
    tbs = soup.find_all('table')
    d = ext_tb2_quanguo(str(tbs[0]))
    if d != '':
        try:
            if 'status' in info:
                xmzt = json.loads(info)['status']
                result = {
                    "xmmc": d['项目名称'],
                    "xmdm": d['项目代码'],
                    "xmdw": "",
                    "xmtz": "",
                    "xmzt": xmzt,
                    "xmdz": "",
                    "xmgk": "",
                    "fabu_time": fabu_time
                }
        except:
            try:
                tr_all = tbs[1].find_all('tr')[1]
                xmzt = tr_all.find_all('td')[-3].text.strip()
                result = {
                    "xmmc": d['项目名称'],
                    "xmdm": d['项目代码'],
                    "xmdw": "",
                    "xmtz": "",
                    "xmzt": xmzt,
                    "xmdz": "",
                    "xmgk": "",
                    "fabu_time": fabu_time
                }
            except:
                pass
    return json.dumps(result, ensure_ascii=False)


def ext_jilinsheng(page, fabu_time, info=None):
    if page is None or page == '':
        return ''
    fabu_time = str(fabu_time)
    soup = BeautifulSoup(page, 'html.parser')
    result, d = {}, {}
    tbs = soup.find_all('table')
    d = ext_tb2_jilinsheng(str(tbs[0]))
    if d != '':
        try:
            if 'jieguo' in info:
                xmzt = json.loads(info)['jieguo']
                result = {
                    "xmmc": d['项目名称：'],
                    "xmdm": d['项目编码：'],
                    "xmdw": d['单位名称：'],
                    "xmtz": d['项目总投资（万元）：'] + '万元',
                    "xmzt": xmzt,
                    "xmdz": d['建设地点：'],
                    "xmgk": d['主要建设规模及内容'],
                    "fabu_time": d['备案日期：']
                }
                print(result)
        except:
            try:
                result = {
                    "xmmc": d['项目名称：'],
                    "xmdm": d['项目编码：'],
                    "xmdw": d['单位名称：'],
                    "xmtz": d['项目总投资（万元）：'] + '万元',
                    "xmzt": d['审核结果：'],
                    "xmdz": d['建设地点：'],
                    "xmgk": d['主要建设规模及内容'],
                    "fabu_time": d['备案日期：']
                }
            except:
                pass

    return json.dumps(result, ensure_ascii=False)


def ext_neimenggusheng(page, fabu_time, info=None):
    if page is None or page == '':
        return ''
    fabu_time = str(fabu_time)
    soup = BeautifulSoup(page, 'html.parser')
    result, d = {}, {}
    tbs = soup.find_all('table')
    d = ext_tb1(str(tbs[0]))
    if d != '':
        try:
            if 'jieguo' in info:
                xmzt = json.loads(info)['jieguo']
                tr_all = tbs[1].find_all('tr')[1]
                fabu_time = tr_all.find_all('td')[-3].text.strip()
                result = {
                    "xmmc": d['项目名称'],
                    "xmdm": d['项目代码'],
                    "xmdw": d['申报单位'],
                    "xmtz": "",
                    "xmzt": xmzt,
                    "xmdz": "",
                    "xmgk": "",
                    "fabu_time": fabu_time
                }
                print(result)
        except:
            try:
                tr_all = tbs[1].find_all('tr')[1]
                fabu_time = tr_all.find_all('td')[-3].text.strip()
                xmzt = tr_all.find_all('td')[-4].text.strip()
                result = {
                    "xmmc": d['项目名称'],
                    "xmdm": d['项目代码'],
                    "xmdw": d['申报单位'],
                    "xmtz": "",
                    "xmzt": xmzt,
                    "xmdz": "",
                    "xmgk": "",
                    "fabu_time": fabu_time
                }
            except:
                pass

    return json.dumps(result, ensure_ascii=False)


def ext_gansusheng(page, fabu_time, info=None):
    fabu_time = str(fabu_time)
    soup = BeautifulSoup(page, 'html.parser')
    result, d = {}, {}
    d = ext_tb1(str(soup.find_all('table')[0]))
    if d != '':
        try:
            fabu_time = soup.find_all('td', attrs={"id": "implement_plan_approval_date"})[0].text.strip()
            if 'jieguo' in info:
                xmzt = json.loads(info)['jieguo']
            else:
                xmzt = ""
            result = {
                "xmmc": d['项目名称'],
                "xmdm": d['项目代码'],
                "xmdw": "",
                "xmtz": d['项目总投资（万元）'] + '万元',
                "xmzt": xmzt,
                "xmdz": d['建设地点'],
                "xmgk": d['建设内容与规模'],
                "fabu_time": fabu_time,
            }
        except:
            pass

    return json.dumps(result, ensure_ascii=False)
