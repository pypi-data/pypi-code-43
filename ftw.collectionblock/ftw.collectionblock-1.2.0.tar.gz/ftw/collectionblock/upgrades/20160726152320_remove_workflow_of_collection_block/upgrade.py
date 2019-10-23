from ftw.upgrade import UpgradeStep
from ftw.upgrade.helpers import update_security_for


class RemoveWorkflowOfCollectionBlock(UpgradeStep):
    """Remove workflow of collection block.
    """

    def __call__(self):
        self.install_upgrade_profile()
        map(
            update_security_for,
            self.objects(
                {'portal_type': 'ftw.collection.CollectionBlock'},
                'Reset security of collection block objects.'
            )
        )
