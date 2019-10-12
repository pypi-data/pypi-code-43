from melthon.middleware import Middleware


class Vegetables(Middleware):
    def before(self, context):
        context['vegetables'] = ['carrot', 'pumpkin', 'potato']
        return context
