from sync.base import BaseSync
from spider.notice import NoticeSpider
from classcard_dataclient.models.notice import Notice


class NoticeSync(BaseSync):
    def __init__(self):
        super(NoticeSync, self).__init__()
        self.page_list = [("http://www.qlshx.sdnu.edu.cn/", "tzgg.htm"),
                          ("http://www.qlshx.sdnu.edu.cn/", "jzyg.htm")]
        self.notice = []

    def crawl(self):
        for page in self.page_list:
            ns = NoticeSpider(page[0], page[1])
            ns.start()
            for target in ns.targets.values():
                notice = Notice(title=target["topic"], content=target["content"])
                self.notice.append(notice)

    def sync(self):
        self.crawl()
        for notice in self.notice:
            self.client.create_notice(self.school_id, notice)
