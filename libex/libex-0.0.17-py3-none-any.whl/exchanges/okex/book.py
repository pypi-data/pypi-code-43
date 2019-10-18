import json
import logging

from ...events import EventType,MarketEvent


logger = logging.getLogger(__name__)

books = {}
events = {}

def register_event(event,cb):

    if 'book10' != event and 'book20' != event:

        return False


    events[event] = cb

def books_snapshot(coin,currency,timestamp,detail):
    logger.debug('books_snapshot, coin:%s ,currency:%s ,timestamp:%s , detail:%s', coin,currency,timestamp,detail)

    key = "%s_%s" % (coin,currency)

    asks = detail.get('asks')
    bids = detail.get('bids')

    books.setdefault(key,{})['asks'] = sorted(asks, key=lambda a: a[0])[0:200]
    books.setdefault(key,{})['bids'] = sorted(bids, key=lambda a: a[0],reverse=True)[0:200]


    touch_book10(coin,currency)
    touch_book20(coin,currency)



def books_update(coin,currency,timestamp,detail):

    logger.debug('books_update: %s' , detail)

    asks = detail.get('asks')
    bids = detail.get('bids')


    logger.debug(f"update depth,{coin}_{currency}, asks:{asks} , bids:{bids} , timestamp:{timestamp}\n")

    key = "%s_%s" % (coin,currency)

    prev_books = json.loads(json.dumps(books))

    if asks:
        curr_asks = books.setdefault(key,{}).setdefault('asks',[])
    
        for item in asks:

            arr = [n for n in curr_asks if n[0] != item[0]]

            if item[1] != '0':
                arr.append(item)

            curr_asks = arr

        sorted_asks = sorted(curr_asks, key=lambda a: a[0])[0:200]  # 按每个元素的第一个数据排序
        books.setdefault(key,{})['asks'] = sorted_asks

    if bids:        
        curr_bids = books.setdefault(key,{}).setdefault('bids',[])

        for item in bids: 

            arr = [n for n in curr_bids if n[0] != item[0]]

            if item[1] != '0':
                arr.append(item)

            curr_bids = arr

    
        sorted_bids = sorted(curr_bids, key=lambda a: a[0],reverse=True)[0:200]  # 按每个元素的第一个数据排序
        books.setdefault(key,{})['bids'] = sorted_bids
      
    books.setdefault(key,{})['timestamp'] = timestamp

    if diff_books(prev_books.get(key).get('asks')[:10] ,prev_books.get(key).get('bids')[:10] , books.get(key).get('asks')[:10] ,books.get(key).get('bids')[:10] ):
        touch_book10(coin,currency)
        touch_book20(coin,currency)

    elif diff_books(prev_books.get(key).get('asks')[:20] ,prev_books.get(key).get('bids')[:20] , books.get(key).get('asks')[:20] ,books.get(key).get('bids')[:20] ):
        touch_book20(coin,currency)


def diff_books(asks1,bids1,asks2,bids2):

    if len(asks1) != len(asks2) or len(bids1) != len(bids2):
        return True

    for i in range(len(asks1)):

        if (asks1[i][0] != asks2[i][0] or asks1[i][1] != asks2[i][1]):
            return True

    for i in range(len(bids1)):
        if (bids1[i][0] != bids2[i][0] or bids1[i][1] != bids2[i][1]):
            return True

    return False
            
def touch_book10(coin,currency):

    logger.debug('touch_book10')


    key = "%s_%s" % (coin,currency)

    book10_cb = events.get('book10')

    logger.debug('events: %s' , events)

    if book10_cb:

        detail = {
            'asks':books.setdefault(key,{})['asks'][0:10],
            'bids':books.setdefault(key,{})['bids'][0:10]
        }

        book10_cb(MarketEvent('book10',detail ,'okex', coin,currency))

def touch_book20(coin,currency):

    logger.debug('touch_book20')


    key = "%s_%s" % (coin,currency)

    book20_cb = events.get('book20')

    if book20_cb:
        detail = {
            'asks':books.setdefault(key,{})['asks'][0:20],
            'bids':books.setdefault(key,{})['bids'][0:20]
        }

        book20_cb(MarketEvent('book20',detail ,'okex', coin,currency))
