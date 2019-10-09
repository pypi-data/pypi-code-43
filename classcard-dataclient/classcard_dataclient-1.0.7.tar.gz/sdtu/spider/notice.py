from spider.base import BaseSpider


class NoticeSpider(BaseSpider):
    @classmethod
    def extract_date(cls, soup):
        try:
            year = soup.find_all("span", class_="year")[0].text
            date = soup.find_all("span", class_="date")[0].text
            year = year.replace(".", "-")
            return "{}-{}".format(year, date)
        except (Exception,):
            return None


class JZSpider(BaseSpider):
    @classmethod
    def extract_date(cls, soup):
        try:
            year = soup.find_all("span", class_="year")[0].text
            date = soup.find_all("span", class_="date")[0].text
            year = year.replace(".", "-")
            return "{}-{}".format(year, date)
        except (Exception,):
            return None

    def process_url(self, url):
        return self.base_url + url
