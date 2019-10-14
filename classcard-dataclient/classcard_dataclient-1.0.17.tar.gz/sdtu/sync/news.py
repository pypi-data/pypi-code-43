from sync.base import BaseSync
from spider.news import NewsSpider
from classcard_dataclient.models.news import News


class NewsSync(BaseSync):
    def __init__(self):
        super(NewsSync, self).__init__()
        self.page_list = [("http://www.sdnu.edu.cn/sdyw/", "cksdywgd.htm"),
                          ("http://www.sdnu.edu.cn/zhxw/", "ckzhxwgd.htm"),
                          ("http://www.sdnu.edu.cn/mtsd/", "ckmtsdgd.htm")]
        self.news = []

    def crawl(self):
        for page in self.page_list:
            ns = NewsSpider(page[0], page[1])
            ns.start()
            for target in ns.targets.values():
                news = News(title=target["topic"], content=target["content"])
                self.news.append(news)

    def sync(self):
        self.crawl()
        for news in self.news:
            self.client.create_news(self.school_id, news)
