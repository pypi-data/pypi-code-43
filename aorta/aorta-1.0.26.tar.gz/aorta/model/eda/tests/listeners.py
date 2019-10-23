import aorta


@aorta.eda.EventListener.register_for('HandledEvent')
class HandledEventListener(aorta.eda.EventListener):
    pass


@aorta.eda.EventListener.register_for('FailingEvent')
class FailingEventListener(aorta.eda.EventListener):

    def handle(self, *args, **kwargs):
        raise Exception


@aorta.eda.EventListener.register_for('FailingOnFinishedEvent')
class FailingOnFinishedEventListener(aorta.eda.EventListener):

    def on_finished(self, *args, **kwargs):
        raise Exception


@aorta.eda.EventListener.register_for('FailingOnExceptionEvent')
class FailingOnExceptionEventListener(aorta.eda.EventListener):

    def handle(self, *args, **kwargs):
        raise Exception

    def on_exception(self, *args, **kwargs):
        raise Exception
