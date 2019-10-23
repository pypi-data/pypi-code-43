from ftw.upgrade import UpgradeStep


class RenderContentNavInDifferentViewlet(UpgradeStep):
    """Render content nav in different viewlet.
    """

    def __call__(self):
        self.install_upgrade_profile()
