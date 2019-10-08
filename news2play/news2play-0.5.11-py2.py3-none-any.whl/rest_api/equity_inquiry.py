from xml.etree import ElementTree
from natural import number
from decimal import *
import datetime
import math
import requests
import csv

webUrl = 'https://fastquote.fidelity.com/service/quote/full?productid=iphone&app=AppleTV&quotetype=D&symbols='


def get_quote_text(company, symbol):
    global audio_version
    stock_response = requests.get(webUrl + symbol)

    try:
        if stock_response.status_code == 200:
            quote_tree = ElementTree.fromstring(stock_response.content)
            quote = quote_tree[1][2]
            ask_price = Decimal(quote.find('LAST_PRICE').text) #ASK_PRICE
            today_close = Decimal(quote.find('PREVIOUS_CLOSE').text)
            changed_percent = Decimal(quote.find('PCT_CHG_TODAY').text)
            changed_net = Decimal(quote.find('NETCHG_TODAY').text)
            lastday_date = datetime.datetime.strptime(quote.find('LAST_DATE').text,'%m/%d/%Y').date()
            today_date = datetime.date.today() #- datetime.timedelta(days=1)
            if (today_date == lastday_date):
                which_day = 'today'
            else:
                which_day = 'yesterday'
            lastday_month = lastday_date.strftime('%B')
            lastday_day = number.ordinal(lastday_date.day)

            lastday_close = today_close - changed_net
            changed_net = abs(changed_net)
            frac, whole = math.modf(changed_net)
            frac = math.ceil(frac * 100)
            changed_net_text = ''
            if (whole != 0):
                changed_net_text = str(int(whole)) +  ' dollars '
            if (frac != 0):
                changed_net_text += str(frac) +  ' cents'


            open_price = quote.find('OPEN_PRICE').text
            day_high = quote.find('DAY_HIGH').text
            day_low = quote.find('DAY_LOW').text
            rating = quote.find('EQUITY_SUMMARY_RATING').text  # very bearish/bearish/neutral/bullish/very bullish
            # score = quote.find('EQUITY_SUMMARY_SCORE').text #0.1 ~ 1.0/1.1 ~ 3.0/3.1 ~ 7.0/7.1 ~ 9.0/9.1 ~ 10.0
            volume = quote.find('AVG_VOL_10_DAY').text  #VOLUME total number of shares traded on one side of the transaction

            if (changed_percent >= 0 and changed_percent < 1):
                up_down = 'rose' #up
            elif (changed_percent >= 1 and changed_percent < 20):
                up_down = 'jumped'
            elif (changed_percent >= 20 and changed_percent < 50):
                up_down = 'climbed'
            elif (changed_percent >= 50):
                up_down = 'soared'
            elif (changed_percent < 0 and changed_percent >= -1):
                up_down = 'fell' #down
            elif (changed_percent < -1 and changed_percent >= -10):
                up_down = 'dropped'
            elif (changed_percent < -10 and changed_percent >= -30):
                up_down = 'declined'
            else: #changed_percent < -30
                up_down = 'plunged'

            changed_percent = abs(changed_percent)
            if (audio_version == 'short'):
                summary = f"{company} opened at {open_price} {which_day}, {up_down} {changed_net_text} or" \
                f" {changed_percent} percent to {ask_price}, the intraday high was {day_high}, and intraday low was {day_low}."
            else:
                summary = f"{company} closed at {lastday_close} on {lastday_month} {lastday_day}, {up_down} by {changed_net_text} or {changed_percent} percent to {ask_price} from previous day's close." \
                f" It opened at {open_price} {which_day}, hit a high of {day_high}, and low of at {day_low}, with {volume} shares traded."

            return summary
        else:
            return f"Sorry, the stock {company} you try to inquirey dosn't exist, please try again."
    except Exception as e:
        print(e)
        return f"Sorry, the inquirey for the stock {company} meets problem, please try again later."

def get_company_symbol(company):
    company_symbol = ''
    company_name = ''
    with open('CompleteCompanyList.csv', mode='r') as f:
        reader = csv.reader(f)
        for num, row in enumerate(reader):
            if company in row[1]:
                company_symbol = row[0]
                company_name = row[1]
                break
            elif company in row[0]:
                company_symbol = row[0]
                company_name = row[1]
                break

    return company_name, company_symbol


def main():
    company_name = 'Apple' # Facebook Apple IBM  Lockheed Boeing Alibaba
    company_name, company_symbol = get_company_symbol(company_name)
    if (company_symbol == ''):
        print('Sorry, the stock ' + company_name + " you try to inquiry doesn't exist, please try again.")
    else:
        print(company_symbol)
        market_summary = get_quote_text(company_name, company_symbol)
        print(market_summary)


if __name__ == '__main__':
    audio_version = 'short'#'short' #'full'
    main()

#Apple Inc. opened at 203.65 yesterday, jumped 4 dollars 63 cents or 2.29 percent to 207.22, the intraday high was 207.23, and intraday low was 203.61.
#Apple Inc. closed at 197.96 on July 22nd, jumped by 4 dollars 63 cents or 2.29 percent to 207.22 from previous day's close. It opened at 203.65 yesterday, hit a high of 207.23, and low of at 203.61, with 18903399 shares traded.

#Boeing Company (The) opened at 376.94 yesterday, dropped 3 dollars 94 cents or 1.04 percent to 373.42, the intraday high was 382.48, and intraday low was 371.89.
#Boeing Company (The) closed at 381.30 on July 22nd, dropped by 3 dollars 94 cents or 1.04 percent to 373.42 from previous day's close. It opened at 376.94 yesterday, hit a high of 382.48, and low of at 371.89, with 4559354 shares traded.

#Facebook, Inc. opened at 199.91 yesterday, jumped 3 dollars 96 cents or 2.00 percent to 202.32, the intraday high was 202.57, and intraday low was 198.81.
#Facebook, Inc. closed at 194.40 on July 22nd, jumped by 3 dollars 96 cents or 2.00 percent to 202.32 from previous day's close. It opened at 199.91 yesterday, hit a high of 202.57, and low of at 198.81, with 13834049 shares traded.

#Netflix, Inc. opened at 312.00 yesterday, dropped 4 dollars 49 cents or 1.42 percent to 310.62, the intraday high was 314.54, and intraday low was 305.81.
#Netflix, Inc. closed at 319.58 on July 22nd, dropped by 4 dollars 49 cents or 1.42 percent to 310.62 from previous day's close. It opened at 312.00 yesterday, hit a high of 314.54, and low of at 305.81, with 10195406 shares traded.

#Columbia Sportswear Company opened at 104.19 today, dropped 1 dollars 79 cents or 1.72 percent to 102.17, the intraday high was 104.40, and intraday low was 102.07.
#Columbia Sportswear Company closed at 105.75 on July 22nd, dropped by 1 dollars 79 cents or 1.72 percent to 102.17 from previous day's close. It opened at 104.19 yesterday, hit a high of 104.40, and low of at 102.07, with 195353 shares traded.

#Columbia Banking System, Inc.
#Columbia Financial, Inc.
