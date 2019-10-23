from ftw.upgrade import UpgradeStep


class ExcludeBlockFromNavigationAndMakeItNotSearchable(UpgradeStep):
    """Exclude block from navigation and make it not searchable.
    """

    def __call__(self):
        self.install_upgrade_profile()
