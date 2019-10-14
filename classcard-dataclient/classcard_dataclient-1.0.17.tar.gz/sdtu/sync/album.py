from sync.base import BaseSync
from spider.album import AlbumSpider
from classcard_dataclient.models.album import Album, Image


class AlbumSync(BaseSync):
    def __init__(self):
        super(AlbumSync, self).__init__()
        self.page_list = [("http://www.student.sdnu.edu.cn/", "list.jsp?urltype=tree.TreeTempUrl&wbtreeid=1016")]
        self.img = []

    def crawl(self):
        for page in self.page_list:
            asp = AlbumSpider(page[0], page[1])
            asp.start()
            for target in asp.targets.values():
                video = Image(name=target["topic"], path=target["content"])
                self.img.append(video)

    def sync(self):
        self.crawl()
        album = Album(name="校园相册集锦")
        for img in self.img:
            album.add_image(img)
        self.client.create_album(self.school_id, album)
