import logging
import json
import zmq
import os

from .util import *

logger = logging.getLogger(__name__)


class TabooJudger:
    def __init__(self, task_setting, attacker_host="127.0.0.1", attacker_port=10086, defender_host="127.0.0.1",
                 defender_port=10087):
        self.task_setting = task_setting
        self.history = {
            "task_setting": task_setting
        }

        self.attacker_context = zmq.Context()
        self.attacker = self.attacker_context.socket(zmq.REQ)
        self.attacker.connect("tcp://%s:%d" % (attacker_host, attacker_port))

        self.attacker.send_json({
            "code": INIT,
            "data": self.task_setting
        })
        data = self.attacker.recv_json()
        if data["code"] != ATTACKER_FEEDBACK:
            logger.error("Unknown code, bad attacker.")
            raise NotImplementedError
        else:
            self.attacker_name = data["data"]

        logger.info("Connected to attacker %s:%d" % (attacker_host, attacker_port))

        self.defender_context = zmq.Context()
        self.defender = self.defender_context.socket(zmq.REQ)
        self.defender.connect("tcp://%s:%d" % (defender_host, defender_port))

        self.defender.send_json({
            "code": INIT,
            "data": self.task_setting
        })
        data = self.defender.recv_json()
        if data["code"] != DEFENDER_FEEDBACK:
            logger.error("Unknown code, bad defender.")
            raise NotImplementedError
        else:
            self.defender_name = data["data"]

        logger.info("Connected to defender %s:%d" % (defender_host, defender_port))

    def select_word(self, word_list):
        self.history["word_list"] = word_list
        logger.info("Word candidate set: %s" % json.dumps(word_list, ensure_ascii=False))
        self.attacker.send_json({
            "code": WORD_SELECT,
            "data": word_list
        })
        data = self.attacker.recv_json()
        if data["code"] != WORD_SELECT:
            logger.error("Unknown code, bad attacker.")
            raise NotImplementedError

        self.word = word_list[data["data"]]
        self.history["select_word"] = self.word
        logger.info("Attacker selects the word: %s" % self.word)

        self.attacker.send_json({
            "code": RECEIVED,
            "data": RECEIVED
        })

    def play_game(self, checker, formatter, ruler, guess_list):
        self.history["sentences"] = []

        while True:
            attack_msg = self.attacker.recv_json()
            if attack_msg["code"] != ATTACK:
                logger.error("Unknown code, bad attacker.")
                raise NotImplementedError

            attack_msg = formatter.format(attack_msg["data"])

            self.history["sentences"].append(attack_msg)
            logger.info("Attacker says: %s" % attack_msg)

            if not ruler.check_available(attack_msg) or not ruler.check_relevance(attack_msg,
                                                                                  self.history["sentences"]):
                logger.error("Bad quality of attacker")
                self.history["result"] = "Bad quality of attacker."
                self.attacker.send_json({
                    "code": BAD_ATTACKER,
                    "data": BAD_ATTACKER
                })
                self.defender.send_json({
                    "code": BAD_ATTACKER,
                    "data": BAD_ATTACKER
                })
                break

            self.defender.send_json({
                "code": DEFEND,
                "data": attack_msg
            })

            defend_msg = self.defender.recv_json()
            if defend_msg["code"] == ACTIVELY_GUESS:
                self.history["guess_word_list"] = guess_list
                self.defender.send_json({
                    "code": GUESS_LIST,
                    "data": self.history["word_list"]
                })
                data = self.defender.recv_json()
                if data["code"] != GUESS:
                    logger.error("Unknown code, bad defender.")
                    raise NotImplementedError
                self.history["guess_id"] = data["data"]
                if guess_list[data["data"]] == self.history["select_word"]:
                    self.attacker.send_json({
                        "code": DEFENDER_WIN,
                        "data": guess_list[data["data"]]
                    })
                    self.defender.send_json({
                        "code": DEFENDER_WIN,
                        "data": DEFENDER_WIN
                    })
                    self.history["result"] = "Defender wins."
                    logger.info("Defender wins")
                    break
                else:
                    self.attacker.send_json({
                        "code": ATTACKER_WIN,
                        "data": {
                            "guess_list": guess_list,
                            "idx": data["data"]
                        }
                    })
                    self.defender.send_json({
                        "code": ATTACKER_WIN,
                        "data": self.word
                    })
                    self.history["result"] = "Attacker wins."
                    logger.info("Attacker wins")
                    break
            elif defend_msg["code"] == DEFEND:
                defend_msg = formatter.format(defend_msg["data"])
                self.history["sentences"].append(defend_msg)
                logger.info("Defender says: %s" % defend_msg)

                if not ruler.check_available(defend_msg) or not ruler.check_relevance(defend_msg,
                                                                                      self.history["sentences"]):
                    logger.error("Bad quality of defender")
                    self.history["result"] = "Bad quality of defender."
                    self.attacker.send_json({
                        "code": BAD_DEFENDER,
                        "data": BAD_DEFENDER
                    })
                    self.defender.send_json({
                        "code": BAD_DEFENDER,
                        "data": BAD_DEFENDER
                    })
                    break

                if checker.check(defend_msg, self.word):
                    self.attacker.send_json({
                        "code": ATTACKER_WIN,
                        "data": defend_msg
                    })
                    self.defender.send_json({
                        "code": ATTACKER_WIN,
                        "data": self.word
                    })
                    self.history["result"] = "Attacker wins."
                    logger.info("Attacker wins")
                    break
                else:
                    self.attacker.send_json({
                        "code": ATTACK,
                        "data": defend_msg
                    })
            else:
                logger.error("Unknown code, bad defender.")
                raise NotImplementedError

        usr_home = os.path.expanduser('~')
        os.makedirs(os.path.join(usr_home, ".taboo"), exist_ok=True)
        json.dump(self.history, open(
            os.path.join(usr_home, ".taboo", "%s_%s_%s" % (self.attacker_name, self.defender_name, time_to_str())),
            "w"), indent=2, ensure_ascii=False)
