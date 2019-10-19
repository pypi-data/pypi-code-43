from juntagrico_webdav.entity.servers import WebdavServer


class WebdavServerDao:

    @staticmethod
    def active_admin_servers():
        return WebdavServer.objects.filter(active=True, type=2)

    @staticmethod
    def active_user_servers():
        return WebdavServer.objects.filter(active=True, type=1)
