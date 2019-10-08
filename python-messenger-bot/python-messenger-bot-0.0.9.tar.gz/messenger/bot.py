import datetime
import threading
import json

from .constant import Constant

from heapq import heappush, heappop, heapify
from messenger.helper import Utils
from messenger.helper.messaging import ButtonTemplate, Message, Postback, QuickReply, Receipt, Response#, GenericTemplate, ReceiptElement, ReceiptAdjustment
from messenger.helper.http import Post, PrioritizedItem

class Bot:
    def __init__(self, page_access_token, **kwargs):
        self.page_access_token = page_access_token
        self.heap = []
        self.limit_count = 0
        self.current_second = 0
        self.limiter = self.start_limiter()

    def rate_limiter(self):
        post = Post(self.page_access_token)
        self.current_second = datetime.datetime.now().second

        while True:
            if self.limit_count < Constant.mps_threshold and self.heap:
                self.limit_count += 1
                heap_pop = heappop(self.heap)
                heap_pop.item[2].info('%s: %s, %s', heap_pop.item[3], heap_pop.item[1], post.send(heap_pop.item[0], heap_pop.item[1]))
            elif self.limit_count == Constant.mps_threshold:
                if self.current_second == datetime.datetime.now().second:
                    while self.current_second == datetime.datetime.now().second:
                        continue
                
                self.current_second = datetime.datetime.now().second
                self.limit_count = 0

    def start_limiter(self):
        limiter = threading.Thread(target=self.rate_limiter)
        limiter.start()

    def unpack_messenger_json(self, json):
        utils = Utils()
        chat_id, chat_time, sender_psid, event = utils.messenger_to_var(json)

        return chat_id, chat_time, sender_psid, event

    def unpack_thread_context_json(self, json):
        utils = Utils()
        psid, signed_request, thread_type, tid = utils.thread_context_to_var(json)

        return psid, signed_request, thread_type, tid

    def send_attachment_file(self, sender_psid, file):
        response = Response()
        response.recipient_psid = sender_psid
        response_text = response.send_attachment_file(file)
        
        post = Post(self.page_access_token)
        post.send(Constant.send_api, response_text)

    def send_button_template(self, logger, sender_psid, button_template):
        response = Response()
        response.recipient_psid = sender_psid
        response_text = response.send_button_template(button_template)
        
        prioritizedItem = PrioritizedItem(1, [Constant.send_api, response_text, logger, 'send_button_template'])
        heappush(self.heap, prioritizedItem)
                
    def send_generic_template(self, logger, sender_psid, generic_template):
        response = Response()
        response.recipient_psid = sender_psid
        response_text = response.send_generic_template(generic_template)

        prioritizedItem = PrioritizedItem(1, [Constant.send_api, response_text, logger, 'send_generic_template'])
        heappush(self.heap, prioritizedItem)

    def send_message(self, logger, sender_psid, text):
        response = Response()
        response.recipient_psid = sender_psid
        response.text = text
        response_text = response.send_message()

        prioritizedItem = PrioritizedItem(1, [Constant.send_api, response_text, logger, 'send_message'])
        heappush(self.heap, prioritizedItem)

    def send_quick_reply(self, logger, sender_psid, text, quick_reply):
        response = Response()
        response.recipient_psid = sender_psid        
        response.text = text
        response_text = response.send_quick_reply(quick_reply)

        prioritizedItem = PrioritizedItem(1, [Constant.send_api, response_text, logger, 'send_quick_reply'])
        heappush(self.heap, prioritizedItem)
        
    def send_receipt(self, logger, sender_psid, receipt):
        response = Response()     
        response.recipient_psid = sender_psid
        response_text = response.send_receipt(receipt)

        prioritizedItem = PrioritizedItem(1, [Constant.send_api, response_text, logger, 'send_receipt'])
        heappush(self.heap, prioritizedItem)

    def send_sender_action(self, sender_psid, logger, sender_action):
        response = Response()
        response.recipient_psid = sender_psid
        
        response_text = response.send_sender_action(sender_action)
        #logger.info("response_text: %s", response_text)

        post = Post(self.page_access_token)
        logger.info("send_sender_action, %s: %s", sender_action, post.send(Constant.send_api, response_text))