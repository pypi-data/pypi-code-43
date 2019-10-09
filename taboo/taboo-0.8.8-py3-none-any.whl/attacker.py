import logging
import zmq
import os
import json

from .util import *

logger = logging.getLogger(__name__)


class TabooAttacker:
    def __init__(self, host="127.0.0.1", port=10086, name="Attacker"):
        self.name = name

        self.context = zmq.Context()
        self.connection = self.context.socket(zmq.REP)
        self.connection.bind("tcp://%s:%d" % (host, port))

        data = self.connection.recv_json()

        if data["code"] == INIT:
            logger.info("Connection to server established.")
            self.task_setting = data["data"]
            self.connection.send_json({
                "code": ATTACKER_FEEDBACK,
                "data": self.name
            })
        else:
            logger.error("Unknown codes from server, raise error")
            raise NotImplementedError

        data = self.connection.recv_json()

        if data["code"] == WORD_SELECT:
            logger.info("Receive word list from judger: %s" % (json.dumps(data["data"])))
            self.word_list = data["data"]
        else:
            logger.error("Unknown codes from server, raise error")
            raise NotImplementedError

    def get_task_setting(self):
        return self.task_setting

    def select_word(self, idx):
        logger.info("Selects the word: %s" % self.word_list[idx])
        self.connection.send_json({
            "code": WORD_SELECT,
            "data": idx
        })

        self.connection.recv_json()

    def attack(self, sent):
        self.connection.send_json({
            "code": ATTACK,
            "data": sent
        })
        data = self.connection.recv_json()
        if data["code"] == DEFENDER_CORRUPT:
            logger.info("Defender corrupts")
        logging.info("Defender says: %s" % data["data"])
        if data["code"] in END_CODE_SET:
            if data["code"] == ATTACKER_WIN:
                logger.info("Attacker wins")
            elif data["code"] == DEFENDER_WIN:
                logger.info("Defender wins")
            elif data["code"] == DRAW:
                logger.info("Draw")

        return data


if __name__ == "__main__":
    os.system("clear")
    logging.basicConfig(format='%(asctime)s - %(levelname)s - %(name)s -   %(message)s',
                        datefmt='%m/%d/%Y %H:%M:%S',
                        level=logging.INFO)

    attacker = TabooAttacker(port=23333)
    attacker.select_word(0)

    while True:
        print("Type your sentence: ", end='')
        sent = input().strip()
        data = attacker.attack(sent)

        if data["code"] in END_CODE_SET:
            break
