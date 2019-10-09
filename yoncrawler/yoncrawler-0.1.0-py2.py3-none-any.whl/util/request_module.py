import requests
from yoncrawler.util.logger import getMyLogger
# TODO : Add Proxy https://www.scrapehero.com/how-to-rotate-proxies-and-ip-addresses-using-python-3/
def basic_request(*args, **kwargs):
    mylogger = getMyLogger()
    mylogger.info(
        f"Crawl {args[0]}"
    )

    try:
        response = requests.get(*args, **kwargs)
        mylogger.info(response)
        encoding = response.encoding
        if encoding == "ISO-8859-1":
            response.encoding = 'euc-kr'

    except Exception as e:
        mylogger.error(
            f"{args[0]} crawl exception\n" + e.__str__()
        )
        return None
    
    return response.text
    # mylogger.debug(self.html)
