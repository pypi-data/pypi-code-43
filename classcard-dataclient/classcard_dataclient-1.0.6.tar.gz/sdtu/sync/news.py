from spider.news import NewsSpider
from classcard_dataclient.models.news import News
from classcard_dataclient.client.action import DataClient


class NewsSync(object):
    def __init__(self):
        self.page_list = [("http://www.sdnu.edu.cn/sdyw/", "cksdywgd.htm"),
                          ("http://www.sdnu.edu.cn/zhxw/", "ckzhxwgd.htm"),
                          ("http://www.sdnu.edu.cn/mtsd/", "ckmtsdgd.htm")]
        self.news = []
        self.client = DataClient()

    def crawl(self):
        for page in self.page_list:
            ns = NewsSpider(page[0], page[1])
            ns.start()
            for target in ns.targets:
                news = News(title=target["topic"], content=target["content"])
                self.news.append(news)

    def sync(self):
        self.crawl()
        for news in self.news:
            self.client.create_news(news)


