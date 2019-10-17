from celery import shared_task

from .settings import MAILER_QUEUE

@shared_task(name='unibox.tasks.send')
def send(sender, recipients, template_slug, context, batch_id = None, object_ids=[], version = "1"):
    """
usage:
from gurutools.bindings.mailer import delegate_send

sender = {
    "id": 1,
    "full_name": "Christo Crampton",
    "email": "christo@appointmentguru.co"
}
recipients = [
    {
        "user_id": 1,
        "relationship_id": 5,
        "full_name": "Christo Crampton",
        "email": "info@38.co.za",
        "phone_number": "+27832566533",
        "email": "info@38.co.za",
        "channel": "practitioner.1",
        "preferred_transport": "email" # or sms or inapp
    },
    {
        "user_id": 1,
        "relationship_id": 5,
        "full_name": "Christo Crampton",
        "email": "info@38.co.za",
        "phone_number": "+27832566533",
        "email": "info@38.co.za",
        "channel": "practitioner.1",
        "preferred_transport": "inapp" # or sms or inapp
    }
]

template_slug='JOIN_SPACE'
context = 	{'space': {'title': 'MySpace'}, 'invitee': {'name': 'Joe Soap', 'email': 'joe@soap.com'}, 'inviter': {'name': 'Joe', 'email': 'joe@soap.com'}, 'membership': {'join_link': 'http://app.appointmentguru.co/#/join/6/?key=1234'}}

args = (sender, recipients, template_slug, context)
send.apply_async(
    args,
    queue='unibox-2',
    serializer='json'
)
    """
    pass


def delegate_send(sender, recipients, template_slug, context, batch_id = None, object_ids=[], version = "1"):
    version_map = {
        "1": send
    }
    args = (
        sender,
        recipients,
        template_slug,
        context,
        batch_id,
        object_ids,
        version
    )
    return getattr(version_map, version, send).apply_async(
        args,
        queue=MAILER_QUEUE,
        serializer='json'
    )
