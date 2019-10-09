import logging
import zmq
import os
import json

from .util import *

logger = logging.getLogger(__name__)


class TabooDefender:
    def __init__(self, host="127.0.0.1", port=10087, name="Defender"):
        self.name = name

        self.context = zmq.Context()
        self.connection = self.context.socket(zmq.REP)
        self.connection.bind("tcp://%s:%d" % (host, port))

        data = self.connection.recv_json()

        if data["code"] == INIT:
            logger.info("Connection to server established.")
            self.task_setting = data["data"]
            self.connection.send_json({
                "code": DEFENDER_FEEDBACK,
                "data": self.name
            })
        else:
            logger.error("Unknown codes from server, raise error")
            raise NotImplementedError

    def get_task_setting(self):
        return self.task_setting

    def receive_msg(self):
        data = self.connection.recv_json()
        if data["code"] == ATTACKER_CORRUPT:
            logger.info("Attacker corrupts")
        logging.info("Attacker says: %s" % data["data"])
        if data["code"] in END_CODE_SET:
            if data["code"] == ATTACKER_WIN:
                logger.info("Attacker wins")
            elif data["code"] == DEFENDER_WIN:
                logger.info("Defender wins")
            elif data["code"] == DRAW:
                logger.info("Draw")

        return data

    def defend(self, sent):
        self.connection.send_json({
            "code": DEFEND,
            "data": sent
        })

    def begin_guessing(self):
        self.connection.send_json({
            "code": ACTIVELY_GUESS,
            "data": ACTIVELY_GUESS
        })

        data = self.connection.recv_json()

        if data["code"] == GUESS_LIST:
            logger.info("Receive word list from judger: %s" % (json.dumps(data["data"])))
            self.word_list = data["data"]
        else:
            logger.error("Unknown codes from server, raise error")
            raise NotImplementedError

        return data["data"]

    def guess_word(self, p):
        self.connection.send_json({
            "code": GUESS,
            "data": p
        })

        data = self.connection.recv_json()

        if data["code"] in END_CODE_SET:
            if data["code"] == ATTACKER_WIN:
                logger.info("Attacker wins")
            elif data["code"] == DEFENDER_WIN:
                logger.info("Defender wins")
            elif data["code"] == DRAW:
                logger.info("Draw")

        return data
