from spider.video import VideoSpider
from classcard_dataclient.models.video import Video
from classcard_dataclient.client.action import DataClient


class VideoSync(object):
    def __init__(self):
        self.page_list = [("http://www.qlshx.sdnu.edu.cn/", "gyss.htm")]
        self.video = []
        self.client = DataClient()

    def crawl(self):
        for page in self.page_list:
            vs = VideoSpider(page[0], page[1])
            vs.start()
            for target in vs.targets.values():
                video = Video(name=target["topic"], path=target["content"])
                self.video.append(video)

    def sync(self):
        self.crawl()
        for video in self.video:
            self.client.create_video(video)


