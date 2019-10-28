
def new_subscriber(sender, instance, *args, **kwargs):
    if kwargs.get('created'):
        instance.get_campaign_token()
