from spider.notice import NoticeSpider
from classcard_dataclient.models.notice import Notice
from classcard_dataclient.client.action import DataClient


class NoticeSync(object):
    def __init__(self):
        self.page_list = [("http://www.qlshx.sdnu.edu.cn/", "tzgg.htm"),
                          ("http://www.qlshx.sdnu.edu.cn/", "jzyg.htm")]
        self.notice = []
        self.client = DataClient()

    def crawl(self):
        for page in self.page_list:
            ns = NoticeSpider(page[0], page[1])
            ns.start()
            for target in ns.targets:
                notice = Notice(title=target["topic"], content=target["content"])
                self.notice.append(notice)

    def sync(self):
        self.crawl()
        for notice in self.notice:
            self.client.create_notice(notice)


