from ftw.upgrade import UpgradeStep


class UpdateDescriptionText(UpgradeStep):
    """Update description text.
    """

    def __call__(self):
        self.install_upgrade_profile()
