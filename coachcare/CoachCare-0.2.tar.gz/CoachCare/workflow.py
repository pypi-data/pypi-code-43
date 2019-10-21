import os
from CoachCare.constants import logging, EXTERNAL_CONFIG_DIR, EMR_CONNECT_INPUT_DIR,\
                                EMR_CONNECT_OUTPUT_DIR, INTERNAL_TEMPLATE_DIR
from CoachCare.templateEngine.channel import Source, Destination
from CoachCare.filewatcher import FileWatcher
from CoachCare.coachcare import CoachCare, Auth
from CoachCare.connectors import FileReader, FileWriter, CoachCareAPIConnector, CoachCareNewUser
#from CoachCare.templateEngine.utils.featurebroker import FeatureBroker
from CoachCare.templateEngine.parsers import Hl7Parser
from CoachCare.restservice import listener
from threading import Thread

logging = logging.getLogger(__name__)
class EmrConnectWorkFlow():
    def __init__(self):
        self.emr_input_dir = EMR_CONNECT_INPUT_DIR # accepts ADT message
        self.emr_output_dir = EMR_CONNECT_OUTPUT_DIR # outputs ORU message
        self.emr_connect_file = None
        self.mbca_thread = None

    def watch_for_mbca_measurement(self, validation=False):
        # Watch for mBCA measurement
        if validation:
            logging.debug("[EmrConnectWorkFlow] FileWatcher WITH validator created")
            mbca_trigger = FileWatcher(path=self.emr_output_dir, validator=self.is_not_ack)
        else:
            logging.debug("[EmrConnectWorkFlow] FileWatcher WITHOUT validator created")
            mbca_trigger = FileWatcher(path=self.emr_output_dir)
        mbca_trigger.pool_interval = 1

        file = mbca_trigger.watch(handler=self.mbca_handler)
        logging.info("[EmrConnectWorkFlow] mBCA measurement found")
        logging.debug("[EmrConnectWorkFlow] mBCA trigger file: " + str(file))

    def mbca_handler(self, file_added="")->str:
        logging.debug("[EmrConnectWorkFlow] mBCA handler {} file added".format(file_added))
        self.emr_connect_file = file_added
        return file_added

    def is_not_ack(self,file_path)->bool:
        logging.debug("[EmrConnectWorkFlow] Verifying {} is NOT an ACK".format(file_path))
        if os.access(file_path, os.R_OK):
            # must read hl7 message to determin if it is an ACK msg type
            msg = Hl7Parser(FileReader(file_path)).parse()
            hl7_msg_type = msg.segment_list[0].msh_9.value
            if hl7_msg_type.upper() == "ACK":
                logging.debug("[EmrConnectWorkFlow] {} IS an ACK NOT processing".format(file_path))        
                return False
            logging.debug("[EmrConnectWorkFlow] {} is NOT an ACK continuing with Workflow".format(file_path))        
            return True 
        else:
            return False

class CoachCareWorkFlow(EmrConnectWorkFlow):
    def __init__(self, token=None):
        super(CoachCareWorkFlow, self).__init__()
        #self.post_measurement_template = EXTERNAL_CONFIG_DIR + "body_measurement_template.json"
        self.post_measurement_template = INTERNAL_TEMPLATE_DIR + "body_measurement_template.json"
        #self.new_user_template = EXTERNAL_CONFIG_DIR + "new_user_adt_template.hl7"
        self.new_user_template = INTERNAL_TEMPLATE_DIR + "new_user_adt_template.hl7"
        self.token = token
        if not token:
            self.token = Auth().authenticate()
        self.cc = CoachCare(token=self.token)

    def run(self, webhook_payload):
        result = None
        new_user_validation = False
        if not webhook_payload.in_db:
            logging.info("[CoachCareWorkFlow] Creating new user")
            self.create_new_user(webhook_payload.account_id, 
                                 webhook_payload.organization_id)
            new_user_validation = True
            logging.info("[CoachCareWorkFlow] Done creating user")

        logging.info("[CoachCareWorkFlow] Watching for mbca measurement in {} folder".format(self.emr_output_dir))
        self.watch_for_mbca_measurement(validation=new_user_validation)

        logging.info("[CoachCareWorkFlow] Posting to coachcare API...")
        result = self.format_and_post_to_coachcare(self.cc)
        if result: 
            logging.info("[CoachCareWorkFlow] Successfully Posted mBCA Measurement to CoachCare")
        else:
            logging.error("[CoachCareWorkFlow] Unsuccessful Post to Coachcare")
        logging.info("\n\n")
        return result

    def format_and_post_to_coachcare(self, coachcare:"CoachCare"):
        """Formats and posts mBCA measurment to C.C."""
        # Setting up Dependencies for templateEngine objects
        logging.debug("[CoachCareWorkFlow] emr_connect_file: " + self.emr_connect_file)
        logging.debug("[CoachCareWorkFlow] Creating source and dest")
        source = Source(InputConnector=FileReader(self.emr_output_dir + self.emr_connect_file))
        logging.debug("[CoachCareWorkFlow] Done creating Source!!!")
        dest = Destination(InputConnector=FileReader(self.post_measurement_template),
                           OutputConnector=CoachCareAPIConnector(api=coachcare))
        logging.info("[CoachCareWorkFlow] Source and Dest created!")
        source.register(dest)
        source.run()
        results = None
        if source.results:
            logging.debug("[CoachCareWorkFlow] Source Results: " + str(source.results[0]))
            results = source.results[0]
        else:
            logging.error("[CoachCareWorkFlow] Source Results: " + str(source.results))
        return results

    def create_new_user(self, ID, org_id):
        """ adds new user to mbca database via ADT message """
        logging.debug("[CoachCareWorkFlow] user id: {}".format(ID))
        source = Source(InputConnector=CoachCareNewUser(api=self.cc, ID=ID, org_id=org_id))
        logging.debug("[CoachCareWorkFlow] Source Created")
        dest = Destination(InputConnector=FileReader(self.new_user_template), 
                           OutputConnector=FileWriter(self.emr_input_dir + 'coach_care_user.hl7'))
        logging.debug("[CoachCareWorkFlow] Destination Created")
        source.register(dest)
        logging.debug("[CoachCareWorkFlow] registered destination with source")
        source.run()
        logging.debug("[CoachCareWorkFlow] Done Running source")
        if source.results:
            return source.results[0]
        return source.results

class MBCAWorkflow(EmrConnectWorkFlow):

    def __init__(self, token=None, version=None):
        super(MBCAWorkflow, self).__init__()
        self.post_measurement_template = INTERNAL_TEMPLATE_DIR + "body_measurement_template.json"
        self.token = token
        if not version:
            self.version = "2.0"
        else:
            self.version = version
        if not token:
            self.token = Auth(version=self.version).authenticate()
        self.cc = CoachCare(token=self.token)
        
    def run(self):
        #watch for mBCA measurement
        while True:
            logging.info("[MBCAWorkflow] Watching for mBCA measurement in {}".format(self.emr_output_dir))
            self.watch_for_mbca_measurement(validation=True)

            # post results to CoachCare API
            logging.info("[MBCAWorkflow] Processing measurement")
            self.format_and_post_to_coachcare(self.cc)

    def format_and_post_to_coachcare(self, coachcare:"CoachCare"):
        # Setting up Dependencies for templateEngine objects
        logging.debug("[MBCAWorkflow] emr_connect_file: " + self.emr_connect_file)
        logging.debug("[MBCAWorkflow] Creating source and dest")
        source = Source(InputConnector=FileReader(self.emr_output_dir + self.emr_connect_file))
        logging.debug("[MBCAWorkflow] Done creating Source!!!")
        dest = Destination(InputConnector=FileReader(self.post_measurement_template),
                           OutputConnector=CoachCareAPIConnector(api=coachcare))
        logging.debug("[MBCAWorkflow] Source and Dest created!")
        source.register(dest)
        source.run()
        results = None
        if source.results:
            if source.results[0] != None:
                logging.info("[MBCAWorkflow] Workflow Complete! Source Results Sucessful: {}\n".format( str(source.results[0])))
                results = source.results[0]
            else:
                logging.error("[MBCAWorkflow] Workflow Complete. Source Results UnSucessful: {}\n".format(str(source.results)))
        else:
            logging.error("[MBCAWorkflow] Workflow Complete. Source Results: {}\n".format(str(source.results)))
        return results
