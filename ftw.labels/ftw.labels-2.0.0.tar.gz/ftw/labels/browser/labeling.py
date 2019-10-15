from Products.Five.browser import BrowserView
from ftw.labels.interfaces import ILabeling
from z3c.json.interfaces import IJSONWriter
from zope.component import getUtility


class Labeling(BrowserView):

    def update(self):
        """Update activated labels.
        """
        labeling = ILabeling(self.context)
        activate_labels = self.request.form.get('activate_labels', [])
        labeling.update(activate_labels)
        self.context.reindexObject(idxs=['labels'])
        return self._redirect()

    def pers_update(self):
        """Update personal labels.
        """
        labeling = ILabeling(self.context)
        label_id = self.request.form.get('label_id')
        activate = self.request.form.get('active')
        if not label_id or activate not in ['True', 'False']:
            return self._redirect()
        activate = not eval(activate)
        ret = labeling.pers_update([label_id], activate)
        self.context.reindexObject(idxs=['labels'])
        writer = getUtility(IJSONWriter)
        self.request.response.setHeader('content-type', 'application/json')
        return writer.write({'ret': (ret and 'ok' or 'nok'), 'new_status': str(activate)})

    def _redirect(self):
        response = self.request.RESPONSE
        referer = self.request.get('HTTP_REFERER')
        if referer and referer is not 'localhost':
            response.redirect(referer)
        else:
            response.redirect(self.context.absolute_url())
