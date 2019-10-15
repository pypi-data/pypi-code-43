from Products.Five.browser.pagetemplatefile import ViewPageTemplateFile
from plone.app.layout.viewlets.common import ViewletBase
from ftw.labels.interfaces import ILabeling
from ftw.labels.interfaces import ILabelSupport
from ftw.labels.utils import title_by_user
from Products.CMFCore.utils import getToolByName


class LabelingViewlet(ViewletBase):

    index = ViewPageTemplateFile('labeling.pt')

    def __init__(self, context, request, view, manager=None):
        super(LabelingViewlet, self).__init__(context, request, view, manager=None)
        self.mtool = getToolByName(self.context, 'portal_membership')

    @property
    def available(self):
        if not self.available_labels:
            return False
        if 'portal_factory' in self.context.absolute_url():
            return False
        if not ILabelSupport.providedBy(self.context):
            return False
        if not self.available_labels[0] and not self.available_labels[1]:
            return False
        return True

    @property
    def active_labels(self):
        return ILabeling(self.context).active_labels()

    @property
    def available_labels(self):
        return ILabeling(self.context).available_labels()

    @property
    def can_edit(self):
        return self.mtool.checkPermission('ftw.labels: Change Labels', self.context)

    @property
    def can_personal_edit(self):
        return self.mtool.checkPermission('ftw.labels: Change Personal Labels', self.context)

    def label_title(self, title, by_user):
        return title_by_user(title, by_user)
