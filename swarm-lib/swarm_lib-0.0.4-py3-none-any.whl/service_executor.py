import logging
from .broker_client import BrokerClient

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s %(levelname)s %(message)s')

class ServiceExecutor():
    def __init__(self, agent, query):
        logging.info("Initializing consumer with query: %s" % query)
        self.state = "initialized"
        self.agent = agent
        self.query = query
        self.contract = None
        self.contract_location = None

    def contract_providers(self):
        if self.search_and_contract() and self.accept_negotiation():
            logging.info("Contract worked")
            return self.contract
        else:
            logging.info("Contract failed at state %s" % self.state)
            return None

    def search_and_contract(self):
        negotiation = BrokerClient.contract(self.agent.description, {"query": self.query})
        if not negotiation:
            self.state = "search_and_contract_failed"
            return None
        else:
            self.state = "waiting_accept_negotiation"
            self.contract, self.contract_location = negotiation
            return self.contract

    def accept_negotiation(self):
        contract = BrokerClient.sign_and_send_tx(self.agent.description, self.agent.keys, self.contract, self.contract_location)
        if not contract:
            self.state = "accept_negotiation_failed"
            return None
        else:
            self.state = "sla_established"
            self.contract = contract
            return contract

    def execute(self, *args, **kwargs):
        if self.state == "sla_established":
            return BrokerClient.smart_use(self.contract, *args, **kwargs)
        else:
            logging.debug("Use service: invalid state '%s'" % self.state)

    def combine_feedbacks(self, broker_feedback, party_feedback, alfa=0.5):
        return alfa * party_feedback + (1 - alfa) * broker_feedback

    def build_reputation_output(self, agreement):
        consumer_reputation = 2.5 # FIXME, e.g., ReputationClientMock.lookup(self.agent.description["@id"])
        broker_feedback = agreement["broker_feedback"]
        consumer_feedback = 2.5 # FIXME
        return {
            "service_id": agreement["provider_id"],
            "broker_feedback": broker_feedback,
            "party_feedback": consumer_feedback,
            "reputation": self.combine_feedbacks(broker_feedback, consumer_feedback, consumer_reputation/5),
        }

    def compute_and_send_reputation(self):
        reputation_tx = {
            "hash_payment_tx": self.contract["tx"]["hash"],
            "party_id": self.agent.description["@id"],
            "party_type": "consumer",
            "output": list(map(self.build_reputation_output, self.contract["sla"])),
            "input": None
        }
        reputation_tx["input"] = {
            "hash_last_tx": "get_last_tx_hash(self.agent.description['@id'])", # FIXME NOW
            "party_sig": "sign_reputation_tx(reputation_tx)", # FIXME NOW
            "party_pub_key": "get_public_key(self.agent.description['@id'])" # FIXME NOW
        }
        logging.debug("Created reputation_tx: %s" % reputation_tx)
        return BrokerClient.send_reputation(self.agent.description, reputation_tx, self.contract_location)

    def get_num_services(self):
        if self.contract:
            return len(self.contract['tx']['content']['output']) - 1
        else:
            logging.debug("get_num_services: contract is None")

    def contract_summary(self):
        if self.contract:
            summary = {
                "consumer_balance": self.contract["tx"]["content"]["output"][0]["value"],
                "providers": [{"provider": o["provider_id"], "price": o["value"]} for o in self.contract["tx"]["content"]["output"][1:]]
            }
            if "sig" in self.contract["tx"]["content"]["input"][0].keys():
                summary["signature"] = self.contract["tx"]["content"]["input"][0]["sig"]

            return summary
