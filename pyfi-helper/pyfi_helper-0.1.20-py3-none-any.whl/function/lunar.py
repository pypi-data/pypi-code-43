from datetime import timedelta

MONTH_NAME = ["", "January", "February", "March", "April", "May", "June", "July", "August", "September", "October",
              "November", "December"]
MONTH_DAYS = [0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31]

LUNAR_CALENDAR_TABLE = [
    0x04AE53, 0x0A5748, 0x5526BD, 0x0D2650, 0x0D9544, 0x46AAB9, 0x056A4D, 0x09AD42, 0x24AEB6, 0x04AE4A,
    # //*1901-1910*/
    0x6A4DBE, 0x0A4D52, 0x0D2546, 0x5D52BA, 0x0B544E, 0x0D6A43, 0x296D37, 0x095B4B, 0x749BC1, 0x049754,
    # //*1911-1920*/
    0x0A4B48, 0x5B25BC, 0x06A550, 0x06D445, 0x4ADAB8, 0x02B64D, 0x095742, 0x2497B7, 0x04974A, 0x664B3E,
    # //*1921-1930*/
    0x0D4A51, 0x0EA546, 0x56D4BA, 0x05AD4E, 0x02B644, 0x393738, 0x092E4B, 0x7C96BF, 0x0C9553, 0x0D4A48,
    # //*1931-1940*/
    0x6DA53B, 0x0B554F, 0x056A45, 0x4AADB9, 0x025D4D, 0x092D42, 0x2C95B6, 0x0A954A, 0x7B4ABD, 0x06CA51,
    # //*1941-1950*/
    0x0B5546, 0x555ABB, 0x04DA4E, 0x0A5B43, 0x352BB8, 0x052B4C, 0x8A953F, 0x0E9552, 0x06AA48, 0x6AD53C,
    # //*1951-1960*/
    0x0AB54F, 0x04B645, 0x4A5739, 0x0A574D, 0x052642, 0x3E9335, 0x0D9549, 0x75AABE, 0x056A51, 0x096D46,
    # //*1961-1970*/
    0x54AEBB, 0x04AD4F, 0x0A4D43, 0x4D26B7, 0x0D254B, 0x8D52BF, 0x0B5452, 0x0B6A47, 0x696D3C, 0x095B50,
    # //*1971-1980*/
    0x049B45, 0x4A4BB9, 0x0A4B4D, 0xAB25C2, 0x06A554, 0x06D449, 0x6ADA3D, 0x0AB651, 0x093746, 0x5497BB,
    # //*1981-1990*/
    0x04974F, 0x064B44, 0x36A537, 0x0EA54A, 0x86B2BF, 0x05AC53, 0x0AB647, 0x5936BC, 0x092E50, 0x0C9645,
    # //*1991-2000*/
    0x4D4AB8, 0x0D4A4C, 0x0DA541, 0x25AAB6, 0x056A49, 0x7AADBD, 0x025D52, 0x092D47, 0x5C95BA, 0x0A954E,
    # //*2001-2010*/
    0x0B4A43, 0x4B5537, 0x0AD54A, 0x955ABF, 0x04BA53, 0x0A5B48, 0x652BBC, 0x052B50, 0x0A9345, 0x474AB9,
    # //*2011-2020*/
    0x06AA4C, 0x0AD541, 0x24DAB6, 0x04B64A, 0x69573D, 0x0A4E51, 0x0D2646, 0x5E933A, 0x0D534D, 0x05AA43,
    # //*2021-2030*/
    0x36B537, 0x096D4B, 0xB4AEBF, 0x04AD53, 0x0A4D48, 0x6D25BC, 0x0D254F, 0x0D5244, 0x5DAA38, 0x0B5A4C,
    # //*2031-2040*/
    0x056D41, 0x24ADB6, 0x049B4A, 0x7A4BBE, 0x0A4B51, 0x0AA546, 0x5B52BA, 0x06D24E, 0x0ADA42, 0x355B37,
    # //*2041-2050*/
    0x09374B, 0x8497C1, 0x049753, 0x064B48, 0x66A53C, 0x0EA54F, 0x06B244, 0x4AB638, 0x0AAE4C, 0x092E42,
    # //*2051-2060*/
    0x3C9735, 0x0C9649, 0x7D4ABD, 0x0D4A51, 0x0DA545, 0x55AABA, 0x056A4E, 0x0A6D43, 0x452EB7, 0x052D4B,
    # //*2061-2070*/
    0x8A95BF, 0x0A9553, 0x0B4A47, 0x6B553B, 0x0AD54F, 0x055A45, 0x4A5D38, 0x0A5B4C, 0x052B42, 0x3A93B6,
    # //*2071-2080*/
    0x069349, 0x7729BD, 0x06AA51, 0x0AD546, 0x54DABA, 0x04B64E, 0x0A5743, 0x452738, 0x0D264A, 0x8E933E,
    # //*2081-2090*/
    0x0D5252, 0x0DAA47, 0x66B53B, 0x056D4F, 0x04AE45, 0x4A4EB9, 0x0A4D4C, 0x0D1541, 0x2D92B5  # //*2091-2099*/
]


# 下面的三个表格是农历数据表 LunarCalendarTable 的结构。总共使用了32位整数的0～23位。
#
# 6 5                4 3 2 1 0
# 表示春节的公历月份 表示春节的公历日期
#
# 19 18 17 16 15 14 13 12 11 10  9  8  7
# 1   2  3  4  5  6  7  8  9 10 11 12 13
# 农历1-13 月大小 。月份对应位为1，农历月大(30 天),为0 表示小(29 天)
#
# 23 22 21 20
# 表示当年闰月月份，值为0 为则表示当年无闰月。

def get_month_days(year, month):
    global MONTH_DAYS
    if month == 2:
        if ((year % 4 == 0) and (year % 100 != 0)) or (year % 400 == 0):
            return 29
        else:
            return 28
    else:
        return MONTH_DAYS[month];


def get_syear_days(syear):
    if ((syear % 4 == 0) and (syear % 100 != 0)) or (syear % 400 == 0):
        return 366
    else:
        return 365


def get_days_of_syear(syear, smonth, sday):
    """ get given day's number of sun year """
    days = 0
    for i in range(1, smonth):
        days += get_month_days(syear, i)
    days += sday
    return days


def get_days_of_lyear(syear, smonth, sday):
    """ get given day's number of the lunar year """
    global LUNAR_CALENDAR_TABLE
    lyear = syear
    spring_month = (LUNAR_CALENDAR_TABLE[syear - 1901] & 0x60) >> 5
    spring_day = (LUNAR_CALENDAR_TABLE[syear - 1901] & 0x1F)
    if (spring_month > smonth) or ((spring_month == smonth) and (spring_day > sday)):
        # the day is before spring festival day, and is previous day in lunar year
        spring_month = (LUNAR_CALENDAR_TABLE[syear - 1901 - 1] & 0x60) >> 5
        spring_day = (LUNAR_CALENDAR_TABLE[syear - 1901 - 1] & 0x1F)
        lyear -= 1
        lunar_days = get_syear_days(lyear) + get_days_of_syear(syear, smonth, sday) \
                     - get_days_of_syear(lyear, spring_month, spring_day)
    else:
        lunar_days = get_days_of_syear(syear, smonth, sday) \
                     - get_days_of_syear(syear, spring_month, spring_day)
    lunar_days += 1  # consider current day
    return lyear, lunar_days


def get_lunar_date(syear, smonth, sday):
    if syear < 1901 or syear > 2099:
        return
        # lunar year, lunar days to spring festival
    lyear, lunar_days = get_days_of_lyear(syear, smonth, sday)
    l_double_month = (LUNAR_CALENDAR_TABLE[lyear - 1901] >> 20) & 0xF

    lmonth = lday = 1
    bits = 19
    month_begin_day = 0
    for lmonth in range(1, 14):
        l_month_big = (LUNAR_CALENDAR_TABLE[lyear - 1901] >> bits) & 0x1
        if month_begin_day + 29 + l_month_big < lunar_days:
            lmonth += 1
            month_begin_day += 29 + l_month_big
        else:
            lday = lunar_days - month_begin_day
            break
        bits -= 1
    if l_double_month:
        # lunar double month adjust
        if l_double_month == lmonth - 1:
            lmonth -= 1
            lmonth += 100  # double month
        elif l_double_month < lmonth - 1:
            lmonth -= 1
    return lyear, lmonth, lday


# ******************************************************************************
# 下面为阴历计算所需的数据,为节省存储空间,所以采用下面比较变态的存储方法.
# ******************************************************************************
# 数组g_lunar_month_day存入阴历1901年到2050年每年中的月天数信息，
# 阴历每月只能是29或30天，一年用12（或13）个二进制位表示，对应位为1表30天，否则为29天
g_lunar_month_day = [
    0x4ae0, 0xa570, 0x5268, 0xd260, 0xd950, 0x6aa8, 0x56a0, 0x9ad0, 0x4ae8, 0x4ae0,  # 1910
    0xa4d8, 0xa4d0, 0xd250, 0xd548, 0xb550, 0x56a0, 0x96d0, 0x95b0, 0x49b8, 0x49b0,  # 1920
    0xa4b0, 0xb258, 0x6a50, 0x6d40, 0xada8, 0x2b60, 0x9570, 0x4978, 0x4970, 0x64b0,  # 1930
    0xd4a0, 0xea50, 0x6d48, 0x5ad0, 0x2b60, 0x9370, 0x92e0, 0xc968, 0xc950, 0xd4a0,  # 1940
    0xda50, 0xb550, 0x56a0, 0xaad8, 0x25d0, 0x92d0, 0xc958, 0xa950, 0xb4a8, 0x6ca0,  # 1950
    0xb550, 0x55a8, 0x4da0, 0xa5b0, 0x52b8, 0x52b0, 0xa950, 0xe950, 0x6aa0, 0xad50,  # 1960
    0xab50, 0x4b60, 0xa570, 0xa570, 0x5260, 0xe930, 0xd950, 0x5aa8, 0x56a0, 0x96d0,  # 1970
    0x4ae8, 0x4ad0, 0xa4d0, 0xd268, 0xd250, 0xd528, 0xb540, 0xb6a0, 0x96d0, 0x95b0,  # 1980
    0x49b0, 0xa4b8, 0xa4b0, 0xb258, 0x6a50, 0x6d40, 0xada0, 0xab60, 0x9370, 0x4978,  # 1990
    0x4970, 0x64b0, 0x6a50, 0xea50, 0x6b28, 0x5ac0, 0xab60, 0x9368, 0x92e0, 0xc960,  # 2000
    0xd4a8, 0xd4a0, 0xda50, 0x5aa8, 0x56a0, 0xaad8, 0x25d0, 0x92d0, 0xc958, 0xa950,  # 2010
    0xb4a0, 0xb550, 0xb550, 0x55a8, 0x4ba0, 0xa5b0, 0x52b8, 0x52b0, 0xa930, 0x74a8,  # 2020
    0x6aa0, 0xad50, 0x4da8, 0x4b60, 0x9570, 0xa4e0, 0xd260, 0xe930, 0xd530, 0x5aa0,  # 2030
    0x6b50, 0x96d0, 0x4ae8, 0x4ad0, 0xa4d0, 0xd258, 0xd250, 0xd520, 0xdaa0, 0xb5a0,  # 2040
    0x56d0, 0x4ad8, 0x49b0, 0xa4b8, 0xa4b0, 0xaa50, 0xb528, 0x6d20, 0xada0, 0x55b0,  # 2050
]

# 数组gLanarMonth存放阴历1901年到2050年闰月的月份，如没有则为0，每字节存两年
g_lunar_month = [
    0x00, 0x50, 0x04, 0x00, 0x20,  # 1910
    0x60, 0x05, 0x00, 0x20, 0x70,  # 1920
    0x05, 0x00, 0x40, 0x02, 0x06,  # 1930
    0x00, 0x50, 0x03, 0x07, 0x00,  # 1940
    0x60, 0x04, 0x00, 0x20, 0x70,  # 1950
    0x05, 0x00, 0x30, 0x80, 0x06,  # 1960
    0x00, 0x40, 0x03, 0x07, 0x00,  # 1970
    0x50, 0x04, 0x08, 0x00, 0x60,  # 1980
    0x04, 0x0a, 0x00, 0x60, 0x05,  # 1990
    0x00, 0x30, 0x80, 0x05, 0x00,  # 2000
    0x40, 0x02, 0x07, 0x00, 0x50,  # 2010
    0x04, 0x09, 0x00, 0x60, 0x04,  # 2020
    0x00, 0x20, 0x60, 0x05, 0x00,  # 2030
    0x30, 0xb0, 0x06, 0x00, 0x50,  # 2040
    0x02, 0x07, 0x00, 0x50, 0x03  # 2050
]

# ==================================================================================

from datetime import date, datetime
from calendar import Calendar as Cal

START_YEAR = 1901


def is_leap_year(tm):
    y = tm.year
    return (not (y % 4)) and (y % 100) or (not (y % 400))


def show_month(tm):
    """

    :param tm: 输入年月日
    :return:
    """
    (ly, lm, ld) = get_lunar_date(tm)
    print()
    print("%d年%d月%d日" % (tm.year, tm.month, tm.day), week_str(tm), )
    print("\t农历：", y_lunar(ly), m_lunar(lm), d_lunar(ld))
    print("日\t一\t二\t三\t四\t五\t六")

    c = Cal()
    ds = [d for d in c.itermonthdays(tm.year, tm.month)]
    count = 0
    for d in ds:
        count += 1
        if d == 0:
            print("\t")
            continue

        (ly, lm, ld) = get_lunar_date(datetime(tm.year, tm.month, d))
        if count % 7 == 0:
            print()

        d_str = str(d)
        if d == tm.day:
            d_str = u"*" + d_str
        print("")
        print(d_str + d_lunar(ld) + u"\t")
    print()


def this_month():
    show_month(datetime.now())


def week_str(tm):
    a = '星期一 星期二 星期三 星期四 星期五 星期六 星期日'.split()
    return a[tm.weekday()]


def d_lunar(ld):
    a = '初一 初二 初三 初四 初五 初六 初七 初八 初九 初十\
    十一 十二 十三 十四 十五 十六 十七 十八 十九 廿十 \
            廿一 廿二 廿三 廿四 廿五 廿六 廿七 廿八 廿九 三十'.split()
    return a[ld - 1]


def m_lunar(lm):
    a = '正月 二月 三月 四月 五月 六月 七月 八月 九月 十月 十一月 十二月'.split()
    return a[lm - 1]


def y_lunar(ly):
    y = ly
    tg = '甲 乙 丙 丁 戊 己 庚 辛 壬 癸'.split()
    dz = '子 丑 寅 卯 辰 巳 午 未 申 酉 戌 亥'.split()
    sx = '鼠 牛 虎 免 龙 蛇 马 羊 猴 鸡 狗 猪'.split()
    return tg[(y - 4) % 10] + dz[(y - 4) % 12] + u' ' + sx[(y - 4) % 12] + u'年'


def date_diff(tm):
    return (tm - datetime(1901, 1, 1)).days


def get_leap_month(lunar_year):
    flag = g_lunar_month[int((lunar_year - START_YEAR) / 2)]
    if (lunar_year - START_YEAR) % 2:
        return flag & 0x0f
    else:
        return flag >> 4


def lunar_month_days(lunar_year, lunar_month):
    if lunar_year < START_YEAR:
        return 30

    high, low = 0, 29
    iBit = 16 - lunar_month

    if lunar_month > get_leap_month(lunar_year) and get_leap_month(lunar_year):
        iBit -= 1

    if g_lunar_month_day[lunar_year - START_YEAR] & (1 << iBit):
        low += 1

    if lunar_month == get_leap_month(lunar_year):
        if g_lunar_month_day[lunar_year - START_YEAR] & (1 << (iBit - 1)):
            high = 30
        else:
            high = 29

    return high, low


def lunar_year_days(year):
    days = 0
    for i in range(1, 13):
        (high, low) = lunar_month_days(year, i)
        days += high
        days += low
    return days


def get_lunar_date(tm):
    """
    输入日期，返回农历日期的年，月，日
    :param tm:
    :return:
    """
    span_days = date_diff(tm)

    # 阳历1901年2月19日为阴历1901年正月初一
    # 阳历1901年1月1日到2月19日共有49天
    if span_days < 49:
        year = START_YEAR - 1
        if span_days < 19:
            month = 11
            day = 11 + span_days
        else:
            month = 12
            day = span_days - 18
        return year, month, day

        # 下面从阴历1901年正月初一算起
    span_days -= 49
    year, month, day = START_YEAR, 1, 1
    # 计算年
    tmp = lunar_year_days(year)
    while span_days >= tmp:
        span_days -= tmp
        year += 1
        tmp = lunar_year_days(year)
        # 计算月
    (foo, tmp) = lunar_month_days(year, month)
    while span_days >= tmp:
        span_days -= tmp
        if month == get_leap_month(year):
            (tmp, foo) = lunar_month_days(year, month)
            if span_days < tmp:
                return 0, 0, 0
            span_days -= tmp
        month += 1
        (foo, tmp) = lunar_month_days(year, month)

        # 计算日
    day += span_days
    return year, month, day


def get_lunar_datetime(cur_date):
    """输入阳历日期，返回农历日期"""
    year, month, day = get_lunar_date(cur_date)
    return datetime(year, month, day)


def spring_month(year):
    """
    输入年份,返回春节所在的月份
    :return:
    """
    jan = datetime(year, 1, 1)
    feb = datetime(year, 2, 1)
    mar = datetime(year, 3, 1)
    apr = datetime(year, 4, 1)
    jan_end = feb + timedelta(days=-1)
    feb_end = mar + timedelta(days=-1)
    mar_end = apr + timedelta(days=-1)
    jan_m, jan_d = get_lunar_date(jan)[1:]
    feb_m, feb_d = get_lunar_date(feb)[1:]
    mar_m, mar_d = get_lunar_date(mar)[1:]
    apr_m, apr_d = get_lunar_date(apr)[1:]
    if jan_m == 12:
        if feb_d > 1:
            return jan.month
        else:
            return feb.month
    elif feb_m == 12:
        if mar_d > 1:
            return feb.month
        else:
            return mar.month
    elif mar_m == 12:
        if apr_d > 1:
            return mar.month
        else:
            return apr.month
    # 如果没有出现12
    elif jan_m == 11:
        if feb_d > 1:
            return jan.month
        else:
            return feb.month
    elif feb_m == 11:
        if mar_d > 1:
            return feb.month
        else:
            return mar.month


def spring_list(begin_year, end_year):
    from datetime import datetime
    import pandas as pd
    sun_date_list = [datetime(year, 2, 1) for year in range(begin_year, end_year + 1)]
    # print(sun_date_list)
    df = pd.Series()
    for sun_date in sun_date_list:
        count = 0
        while True:
            if count > 100:
                break
            lunar_date = get_lunar_datetime(sun_date)
            if lunar_date > datetime(sun_date.year, 1, 1):  # 和春节比较
                sun_date = sun_date + timedelta(days=-1)
            elif lunar_date < datetime(sun_date.year, 1, 1):
                sun_date = sun_date + timedelta(days=1)
            else:
                break
        df.loc[sun_date] = lunar_date
    return df.dropna()


if __name__ == "__main__":
    y, m, d = 2018, 9, 13
    # print("Sun calendar 2010-9-13 == Lunar calendar ", get_lunar_datetime(datetime(y, m, d)))
    # this_month()
    print(spring_list(2002, 2018))
    # spring_month(2003)
    # for i in range(1990, 2020):
    #     print(str(i) + ":" + str(spring_month(i)))
