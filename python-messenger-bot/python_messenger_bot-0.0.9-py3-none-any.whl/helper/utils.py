from messenger.helper.messaging import Attachment, Message, Postback, QuickReply

class Utils:
    def messenger_to_var(self, json):
        obj = json['object']
        chat_id = chat_time = sender_psid = event = ''
        attachment = Attachment()
        message = Message()
        postback = Postback()
        quick_reply = QuickReply()

        #there may be multiple if batched: developers.facebook.com/docs/messenger-platform/getting-started/quick-start
        #not handled, no batch processing yet
        #for entry in json['entry']:
        entry = json['entry'][0]
            
        chat_id = entry['id']
        chat_time = entry['time']

        webhook_event = entry['messaging'][0]
        sender_psid = webhook_event['sender']['id']
        #recipient_psid not handled

        if webhook_event.get('message'):
            if webhook_event['message'].get('quick_reply'):
                quick_reply.json_to_var(webhook_event['message'])
                event = quick_reply
            elif webhook_event['message'].get('attachments'):
                attachment.json_to_var(webhook_event['message'])
                event = attachment
            else:
                message.json_to_message(webhook_event['message'])
                event = message
        elif webhook_event.get('postback'):
            postback.json_to_message(webhook_event['postback'])
            event = postback

        return chat_id, chat_time, sender_psid, event
    def thread_context_to_var(self, json):
        psid = json['psid']
        signed_request = json['signed_request']
        thread_type = json['thread_type']
        tid = json['tid']

        return psid, signed_request, thread_type, tid