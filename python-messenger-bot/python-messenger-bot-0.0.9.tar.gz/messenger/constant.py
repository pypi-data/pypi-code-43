class Constant:
    default_api_version = 4.0
    send_api = 'https://graph.facebook.com/v%s/me/messages'%default_api_version
    insights_api = 'https://graph.facebook.com/v%s/me/insights'%default_api_version
    mps_threshold = 30
    
    class attachment_type:
        audio = 'AUDIO'
        video = 'VIDEO'
        image = 'IMAGE'
        file = 'FILE'
        template = 'TEMPLATE'

    class messaging_type:
        response = 'RESPONSE'
        update = 'UPDATE'
        message_tag = 'MESSAGE_TAG'

    class sender_action:
        mark_seen = 'mark_seen'
        typing_on = 'typing_on'
        typing_off = 'typing_off'

    class template_type:
        receipt = 'receipt'
        button = 'button'
        generic = 'generic'