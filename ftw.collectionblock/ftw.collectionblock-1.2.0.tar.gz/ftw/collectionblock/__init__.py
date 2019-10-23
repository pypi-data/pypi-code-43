from zope.i18nmessageid import MessageFactory


_ = MessageFactory('ftw.collectionblock')


def initialize(context):
    """Required for being able to uninstall this product.
    """
