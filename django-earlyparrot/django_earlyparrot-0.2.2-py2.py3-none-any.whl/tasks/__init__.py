from celery import current_app as app

from .campaign import CampaignSubscribeTask
from .subscriber import SubscriberGetTokenTask

app.tasks.register(CampaignSubscribeTask())
app.tasks.register(SubscriberGetTokenTask())
