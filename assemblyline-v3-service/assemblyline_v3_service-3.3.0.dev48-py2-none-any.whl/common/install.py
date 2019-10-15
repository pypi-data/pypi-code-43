class SiteInstaller(object):

    @staticmethod
    def check_version(serv, vers):
        from pkg_resources import get_distribution
        try:
            if get_distribution(serv).version == vers:
                return True
            return False
        except Exception:
            return False