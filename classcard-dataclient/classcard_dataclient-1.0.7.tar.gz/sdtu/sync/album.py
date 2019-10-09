from spider.album import AlbumSpider
from classcard_dataclient.models.album import Album, Image
from classcard_dataclient.client.action import DataClient
from basedata.constants import SCHOOL_NAME
from basedata.loggerutils import logging

logger = logging.getLogger(__name__)


class AlbumSync(object):
    def __init__(self):
        self.page_list = [("http://www.student.sdnu.edu.cn/", "list.jsp?urltype=tree.TreeTempUrl&wbtreeid=1016")]
        self.img = []
        self.client = DataClient()

    def crawl(self):
        for page in self.page_list:
            asp = AlbumSpider(page[0], page[1])
            asp.start()
            for target in asp.targets.values():
                video = Image(name=target["topic"], path=target["content"])
                self.img.append(video)

    def sync(self):
        code, school = self.client.get_school_by_name(SCHOOL_NAME)
        if code:
            logger.error("Error: get school info, Detail: {}".format(school))
        school_id = school.get("uuid")
        self.crawl()
        album = Album(name="校园相册集锦")
        for img in self.img:
            album.add_image(img)
        self.client.create_album(school_id, album)
