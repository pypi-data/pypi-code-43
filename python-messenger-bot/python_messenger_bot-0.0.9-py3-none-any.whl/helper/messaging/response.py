from messenger.constant import Constant

class Response:

    def __init__(self, **kwargs):
        self.recipient_psid = ''
        
        return super().__init__(**kwargs)
        
    def send_attachment_file(self, file):
        response = {}

        if not self.recipient_psid:
            print('recipient cannot be blank')
            return ''

        response['recipient'] = {'id' : self.recipient_psid}
        response['message'] = {}
        response['message']['attachment'] = {}
        response['message']['attachment']['type'] = Constant.attachment_type.file
        response['message']['attachment']['payload'] = {}
        
        if not file:
            print('payload_url cannot be blank')
            return ''

        response['message']['attachment']['payload']['url'] = file
        response['message']['attachment']['payload']['is_reusable'] = True

        return response    
    def send_button_template(self, button_template):
        response = {}

        if not self.recipient_psid:
            print('recipient cannot be blank')
            return ''

        response['recipient'] = {'id' : self.recipient_psid}
        response['message'] = {}
        response['message']['attachment'] = {}
        response['message']['attachment']['type'] = Constant.attachment_type.template
        response['message']['attachment']['payload'] = {}

        response['message']['attachment']['payload']['template_type'] = Constant.template_type.button
        response['message']['attachment']['payload']['text'] = button_template.payload_text
        
        response['message']['attachment']['payload']['buttons'] = []

        for button in button_template.payload_buttons:
            btn = {}

            btn['type'] = button.type
            btn['title'] =  button.title

            if button.type == 'web_url':
                btn['url'] = button.url
                btn['webview_height_ratio'] =  button.webview_height_ratio
                btn['messenger_extensions'] =  button.messenger_extensions
            else:
                btn['payload'] =  button.payload

            response['message']['attachment']['payload']['buttons'].append(btn)

        return response
    def send_generic_template(self, generic_template):
        response = {}
        
        if not self.recipient_psid:
            print('recipient cannot be blank')
            return ''

        response['recipient'] = {'id' : self.recipient_psid}
                
        response['message'] = {}
        response['message']['attachment'] = {}
        response['message']['attachment']['type'] = Constant.attachment_type.template

        response['message']['attachment']['payload'] = {}
        response['message']['attachment']['payload']['template_type'] = Constant.template_type.generic
        
        response['message']['attachment']['payload']['elements'] = []

        for pe in generic_template.payload_elements:
            element = {}

            element['title'] = pe.title
            
            if pe.subtitle:
                element['subtitle'] = pe.subtitle
            if pe.image_url:
                element['image_url'] = pe.image_url
            #if not pe['default_action']:
            #    element['default_action'] = pe.default_action

            if len(pe.buttons) > 0:
                element['buttons'] = []

                for button in pe.buttons:
                    btn = {}

                    btn['type'] = button.type
                    btn['title'] =  button.title

                    if button.type == 'web_url':
                        btn['url'] = button.url
                        btn['webview_height_ratio'] =  button.webview_height_ratio
                        btn['messenger_extensions'] =  button.messenger_extensions
                    else:
                        btn['payload'] =  button.payload

                    element['buttons'].append(btn)

            response['message']['attachment']['payload']['elements'].append(element)

        return response
    def send_message(self):
        response = {}

        response['messaging_type'] = Constant.messaging_type.response
        
        if not self.recipient_psid:
            print('recipient cannot be blank')
            return ''

        response['recipient'] = {'id' : self.recipient_psid}

        if self.text:
            response['message'] = {'text' : self.text}

        return response

    def send_quick_reply(self, quick_reply):
        response = {}

        response['messaging_type'] = Constant.messaging_type.response
        
        if not self.recipient_psid:
            print('recipient cannot be blank')
            return ''

        response['recipient'] = {'id' : self.recipient_psid}

        response['message'] = {}
        response['message']['text'] = self.text

        response['message']['quick_replies'] = []

        for qr in quick_reply:
            response['message']['quick_replies'].append({'content_type': qr.content_type,
                                                         'title':qr.title,
                                                         'payload': qr.payload,
                                                         'image_url': qr.image_url})

        return response
    def send_receipt(self, receipt):
        
        if not self.recipient_psid:
            print('recipient cannot be blank')
            return ''

        response = {}
        response['recipient'] = {'id' : self.recipient_psid}

        response['message'] = {}

        response['message']['attachment'] = {}
        response['message']['attachment']['type'] = Constant.attachment_type.template

        response['message']['attachment']['payload'] = {}
        response['message']['attachment']['payload']['template_type'] = Constant.template_type.receipt
        response['message']['attachment']['payload']['recipient_name'] = receipt.payload_recipient_name
        response['message']['attachment']['payload']['order_number'] = receipt.payload_order_number
        response['message']['attachment']['payload']['currency'] = receipt.payload_currency
        response['message']['attachment']['payload']['payment_method'] = receipt.payload_payment_method
        #response['message']['attachment']['payload']['order_url']
        response['message']['attachment']['payload']['timestamp'] = receipt.payload_timestamp

        response['message']['attachment']['payload']['address'] = {}
        response['message']['attachment']['payload']['address']['street_1'] = receipt.payload_address_street1
        response['message']['attachment']['payload']['address']['street_2'] = receipt.payload_address_street2
        response['message']['attachment']['payload']['address']['city'] = receipt.payload_address_city
        response['message']['attachment']['payload']['address']['postal_code'] = receipt.payload_address_postal_code
        response['message']['attachment']['payload']['address']['state'] = receipt.payload_address_state
        response['message']['attachment']['payload']['address']['country'] = receipt.payload_address_country

        response['message']['attachment']['payload']['summary'] = {}
        response['message']['attachment']['payload']['summary']['subtotal'] = receipt.payload_summary_subtotal
        response['message']['attachment']['payload']['summary']['shipping_cost'] = receipt.payload_summary_shipping_cost
        response['message']['attachment']['payload']['summary']['total_tax'] = receipt.payload_summary_total_tax
        response['message']['attachment']['payload']['summary']['total_cost'] = receipt.payload_summary_total_cost

        response['message']['attachment']['payload']['adjustments'] = []

        response['message']['attachment']['payload']['elements'] = []

        for adjustment in receipt.payload_adjustments:
            response['message']['attachment']['payload']['adjustments'].append({'name': adjustment.name,
                                                         'amount':adjustment.amount})
            
        for element in receipt.payload_elements:
            response['message']['attachment']['payload']['elements'].append({'title': element.title,
                                                         'subtitle': element.subtitle,
                                                         'quantity': element.quantity,
                                                         'price': element.price,
                                                         'currency': element.currency,
                                                         'image_url': element.image_url})

        return response
    def send_sender_action(self, sender_action):
        response = {}
        
        if not self.recipient_psid:
            print('recipient cannot be blank')
            return ''

        response['recipient'] = {'id' : self.recipient_psid}
        response['sender_action'] = sender_action

        return response