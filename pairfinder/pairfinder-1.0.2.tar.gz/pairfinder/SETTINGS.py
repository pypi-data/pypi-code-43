from datetime import datetime

# upper, lower band (Bollinger)
K_ARR = [0.5, 1, 1.5, 2]

#---------------------------------------------------------------------------------------------------------------------
# Peer Analysis
#---------------------------------------------------------------------------------------------------------------------
# Analysis
METHODS = ['Ratio', 'zscore', 'DROsMA'] #['ratio', 'ROsMA', 'OLS', 'TLS', 'KF', 'NPI']
FROM_ = "2015-01-01" #datetime.fromordinal(datetime(1900, 1, 1).toordinal() + int(worksheet.cell_value(1, 1)) - 2).strftime("%Y-%m-%d")#"2015-01-01"#"2015-01-01"

TO_ = datetime.now().strftime("%Y-%m-%d") #datetime.fromordinal(datetime(1900, 1, 1).toordinal() + int(worksheet.cell_value(2, 1)) - 2).strftime("%Y-%m-%d")
ROLLING = True
WINDOW = 365#int(worksheet.cell_value(3, 1))

ADDITIONAL_FEATURES = ['AVG_TRADING_VALUE', 'DIVIDEND_YIELD']
#---------------------------------------------------------------------------------------------------------------------
# Exporting
#-------------------key, name, width, format, description--------------------------------------------------------------
PLOT_FROM_ = FROM_
PLOT_XAXIS_N_LOCATOR = 10

SHEET_HEIGHT = 210
SHEET_RECIPES = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 13, 14, 15, 16, 17, 18, 19, 20]
SHEET_VARIABLES = [['LONG', 'Y'], ['SHORT', 'X']]#[['COMM', '보통주'], ['PREF', '우선주']]#[['X', '독립변수'], ['Y', '종속변수']] #

SHEET_COOKBOOK  =   {0:["NO.", 6.38, "numeric", "순서"],
                     1:["SYMBOL", 15, "string", "종목코드"],
                     2:["SYMBOL", 15, "string", "종목코드"],
                     3:["NAME", 15, "string", "종목명"],
                     4:["NAME", 15, "string", "종목명"],

                     5:["SPREAD", 13.38, "float_third_dec", "스프레드"],

                     6:["PRICE_PLOT", 101, "string", "가격 그래프"],
                     7:["SPREAD_PLOT", 101, "string", "스프레드 그래프"],
                     8:["BOX_PLOT", 40, "string", "스프레드 박스 그래프"],
                     9:["DIST_PLOT", 40, "string", "스프레드 분포 그래프"],
                     10:["LOG_TLS_PLOT", 40, "string", "로그 주가 Total Least Squares 회귀 그래프"],

                     11:["CLOSE", 15, "string", "심볼"],
                     12:["CLOSE", 15, "string", "심볼"],

                     13:["CORRELATION", 15, "string", "심볼"],

                     14:["P_VALUE", 15, "float_second_dec", "스프레드의 통계값이 실제로 관측된 값 이상일 확률"
                                                            "(0.05 이하)"],
                     15:["HURST_EXPNT", 15, "float_second_dec", "스프레드 허스트 지수"],
                     16:["HALF_LIFE", 15, "float_second_dec", "스프레드 반감기"],

                     17:["AVG_TRADING_VALUE", 21, "integer", "30일 평균 거래대금"],
                     18:["AVG_TRADING_VALUE", 21, "integer", "30일 평균 거래대금"],
                     19:["DIVIDEND_YIELD", 16.63, "float_rate", "배당 수익률(12M)"],
                     20:["DIVIDEND_YIELD", 16.63, "float_rate", "배당 수익률(12M)"]}

def cook_sheet(cookbook, recipes, variables):
    sheet_columns = {}
    x_column, y_column = variables[0][0], variables[1][0]
    x_description, y_description = variables[0][1], variables[1][1]

    for recipe in recipes:
        target = cookbook[recipe]
        if recipe in [1, 3, 11, 17, 19]:
            target[0] = x_column + '_' + target[0]
            target[3] = x_description + ' ' + target[3]
        elif recipe in [2, 4, 12, 18, 20]:
            target[0] = y_column + '_' + target[0]
            target[3] = y_description + ' ' + target[3]

        sheet_columns[recipe] = target
    return sheet_columns

SHEET_COLUMNS = cook_sheet(SHEET_COOKBOOK, SHEET_RECIPES, SHEET_VARIABLES)

