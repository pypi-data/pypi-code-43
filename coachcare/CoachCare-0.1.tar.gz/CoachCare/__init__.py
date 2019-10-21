from CoachCare.constants import logging, LISTENER_OUTPUT_DIR, BASE_DIR
from CoachCare.templateEngine.channel import Source, Destination
from CoachCare.filewatcher import FileWatcher
from CoachCare.restservice.listener import listener
from CoachCare.coachcare import CoachCare, Auth
from CoachCare.connectors import FileReader, FileWriter, CoachCareAPIConnector, CoachCareNewUser
from CoachCare.templateEngine.utils.featurebroker import FEATURES
from threading import Thread
import json

"""
class WorkFlow():
    def __init__(self):
        #read from config
        self.emr_input_dir = "C:\\KisToSecaSuc\\" #accepts ADT message
        self.emr_output_dir = "C:\\SecaSucToKis\\" #sends ORU message
        self.post_measurement_template = BASE_DIR + "tests\\test_data\\body_measurement_template_minimal.json"
        self.handler_result = None
        self.emr_connect_file = None

    def run(self):
        # need handler for listener-watcher
        while True:
            print("self.base_dir: ", self.base_dir)
            print("Authenticating to API")
            token = Auth().authenticate() 
            coachcare = CoachCare(token=token)
            print("listening for webhook...")
            self.listen_for_webhook()
            print("Getting results for webhook...")
            self.get_webhook_results()
            print("watching for mbca measurement")
            self.watch_for_mbca_measurement()
            print("Posting to coachcare API...")
            self.format_and_post_to_coachcare(coachcare)
            print("Done posing to CoachCARE")

    def get_webhook_results(self):
        if self.handler_result:
            acnt_id = self.handler_result["account"]["id"]
            acnt_type = self.handler_result["account"]["type"]["id"]
            org_id = self.handler_result["organization"]["id"]
            print("Recieved: ", json.dumps(self.handler_result, indent=2))
            # Checking if Patient ID in DB
            if not self.handler_result["in_db"]:
                self.create_new_user(acnt_id)

    def watch_for_mbca_measurement(self):
        # Watch for mBCA measurement
        print("Watching {}".format(self.emr_output_dir))
        mbca_trigger = FileWatcher(path=self.emr_output_dir)
        #mbca_trigger_thread = Thread(target=mbca_trigger.watch, kwargs={"handler":self.mbca_handler})
        ret = mbca_trigger.watch(handler=self.mbca_handler)
        print("mbca_trigger returned: ", ret)

        #print("Starting mbca_trigger thread")
        #mbca_trigger_thread.start()
        #print("Joining mbca_trigger thread")
        #mbca_trigger_thread.join()
        print("Done")

    def listen_for_webhook(self):
        listener_thread = Thread(target=listener.run, kwargs={"port":5002, "use_reloader":False, "debug":True})
        trigger = FileWatcher(path=LISTENER_OUTPUT_DIR, file_type="data", target=self.webhook_handler)
        fw_thread = Thread(target=trigger.watch, kwargs={"handler":self.webhook_handler})
        fw_thread.start()
        listener_thread.start()
        fw_thread.join()

    def format_and_post_to_coachcare(self, coachcare):
        #Setting up Dependencies for templateEngine objects
        FEATURES.Provide("Source_InputConnector", FileReader(self.emr_output_dir + self.emr_connect_file))
        FEATURES.Provide("Destination_InputConnector", FileReader(self.post_measurement_template))
        FEATURES.Provide("Destination_OutputConnector", CoachCareAPIConnector(api=coachcare))

        # /////////// Converts ORU to JSON Template ////////////
        # ////////// and Post Json message to C.C API   ////////////
        source = Source()
        dest = Destination()
        source.register(dest)
        source.run()
        print("dont running source")

    def create_new_user(self, ID):
        #adds new user to mbca database via ADT message
        #//////// These all need to be read from config files ////
        new_user_template = BASE_DIR + "tests\\test_data\\new_user_adt_template.hl7"
        seca_to_kis_dir = "C:\SecaSucToKis"
        kis_to_seca_suc = "C:\KisToSecaSuc\coach_care_user.hl7"
        # note: creds will be read from config file

        logging.debug("[Main::create_new_user] Creating new user!!")
        token = Auth().authenticate()
        coachcare = CoachCare(token=token)

        FEATURES.Provide("Source_InputConnector", CoachCareNewUser(api=coachcare, ID=ID))
        FEATURES.Provide("Destination_InputConnector", FileReader(new_user_template))
        FEATURES.Provide("Destination_OutputConnector", FileWriter(kis_to_seca_suc))
        source = Source()
        dest = Destination()
        source.register(dest)
        source.run()

    def mbca_handler(self, file_added=""):
        print("Setting emr_connect_file")
        dir = self.emr_output_dir + file_added
        self.emr_connect_file = file_added
        with open(dir, "r") as f:
            data = "\r".join(f.readlines())
        return file_added

    def webhook_handler(self, file_added=""):
        # gets the info from webhook file
        res = {}
        path = LISTENER_OUTPUT_DIR +file_added
        try:
            with open(path) as f:
                #set instance attribute 
                self.handler_result = json.load(f)
            return res
        except FileNotFoundError:
            print("File not found")
        except json.decoder.JSONDecodeError:
            print("Could not decode json file {}".format(path))
"""
