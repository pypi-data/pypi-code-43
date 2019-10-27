from slackclient import SlackClient


def get_client(**kwargs):
    return SlackClient(**kwargs)
