from abc import ABC, abstractmethod
from CoachCare.constants import logging, BASE_DIR, EMR_CONNECT_OUTPUT_DIR
import json
import psycopg2
import os

logging = logging.getLogger(__name__)
class InputConnector():

    def read(self):
        raise NotImplementedError

class OutputConnector(ABC):

    @abstractmethod
    def write(self, data):
        raise NotImplementedError

class CoachCareNewUser(InputConnector):
    def __init__(self, api, ID, org_id=None):
        self.cc = api
        self.id = ID
        self.org_id = org_id
        self.file_type = "json"
        logging.debug("[CoachCareNewuser] api({})".format(api))
        logging.debug("[CoachCareNewuser] ID({})".format(ID))

    def read(self):
        #Post account association (associate new account with organization id)
        #self.__post_association()
        return self.__get_account()

    def __post_association(self):
        logging.debug("[CoachCareNewUser] Posting account id: {} association with organization id: {}".format(self.id, self.org_id))
        association_data = {"account":self.id, "organization":self.org_id}
        res = self.cc.post_association(**association_data)
        if not res:
            logging.error("[CoachCareNewuser] FAILED to post association: {} to API".format(association_data))
        if res:
            logging.debug("[CoachCareNewUser] Association Post results:{} ".format(str(res)))
            logging.debug("[CoachCareNewUser] Done posting association")

    def __get_account(self):
        logging.debug("[CoachCareNewUser] Gettting account by id:{}".format(self.id))
        results = self.cc.get_account_by_id(self.id)
        if not results:
            logging.error("[CoachCareNewuser] FAILED get account by id:{}".format(self.id))
        else:
            results = json.dumps(results)
            #print("[CoachCareNewuser] results: {}".format(results))
        return results

class FileReader(InputConnector):
    def __init__(self, file_path):
        self.path = file_path
        self.file_type = file_path.split(".")[1].lower()

    def read(self):
        logging.debug("[FileReader] reading path: " + str(self.path))
        data = None
        try:
            data = self._read_data(self.path)
        except Exception as e:
            # handle files moved to "processed" folder.
            if EMR_CONNECT_OUTPUT_DIR in self.path:
                data = self._check_emr_connect_process_folder()
            else:
                logging.error("[FileReader] "+str(e))
        return data

    def _check_emr_connect_process_folder(self):
        logging.debug("[FileReader] Checking Processed folder for hl7 message")
        processed_folder = "Processed"
        try:
            filename = self.path.split("\\")[-1]
            processed_folder = os.path.join(EMR_CONNECT_OUTPUT_DIR, processed_folder)
            processed_folder = os.path.join(processed_folder, filename)
            data = self._read_data(processed_folder)
            logging.debug("[FileReader] Found file in processed folder({})".format(processed_folder))
            return data
        except Exception as e:
            logging.debug("[FileReader] Error accessing {}\\{}".format(EMR_CONNECT_OUTPUT_DIR, filename))
            return None

    def _read_data(self,path):
        data = None
        with open(path, "r") as f:
            if self.file_type.lower() == "hl7":
                data = "\r".join(f.readlines())
            else:
                data = "".join(f.readlines())
        return data

    def test_read(self):
        try:
            with open(self.path,"r"):
                pass
            return True
        except FileNotFoundError:
            return False

class FileWriter(OutputConnector):
    def __init__(self, file_path):
        self.path = file_path
        logging.debug("[FileWriter] file_path: {}".format(file_path))
        try:
            self.file_type = file_path.split(".")[1].lower()
        except:
            self.file_type = ""

    def write(self, data):
        logging.debug("[FileWriter] write called")
        with open(self.path, "w") as f:
            #logging.debug("[FileWriter] file_type: " + self.file_type )
            if self.file_type.lower() == "json":
                #logging.debug("[FileWriter] writing json")
                json.dump(data, f)
            else:
                if data:
                    #logging.debug("[FileWriter] writing {} type".format(self.file_type))
                    f.write(data)
                else:
                    logging.error("[FileWriter] NO DATA TO WRITE!!!!")

    def test_write(self):
        try:
            with open(self.path, "w"):
                pass
            return True
        except FileNotFoundError:
            return False

class DB(InputConnector):
    def __init__(self, **params):
        self._params = params
        self._conn = None

    def read(self):
        raise NotImplementedError

    def _connect(self):
        if self._params == None:
            logging.error("Can't connect to DB without Parameters specified")
        if self._conn == None or self._conn.closed:
            self._conn = psycopg2.connect(**self._params)

class DbReader(DB):
    def __init__(self, **params):
        DB.__init__(self, **params)
        self._connect()

    def read(self):
        logging.info("[DbReader] reading...")
        with self._conn.cursor() as cur:
            #cur.execute("""SELECT table_name FROM information_schema.tables
            #                        WHERE table_schema = 'public' """)
            cur.execute('SELECT (id, doctor,dateofbirth,alternatevisitid) FROM patient')
            res = cur.fetchall()
            print("[DbReader] res: ", res)
        self._conn.close()

    def has_user_by_id(self, ID):
        logging.info("[DbReader] Checking if user id({}) in DB".format(ID))
        self._connect()
        query = """SELECT id FROM patient WHERE id = %s AND deleted = 0"""
        with self._conn.cursor() as cur:
            cur.execute(query, (str(ID),))
            results = []
            for res in cur.fetchall():
                results.append(res)
            if results:
                return results
            else:
                logging.debug("[DbReader] returning None")
                return None

class CoachCareAPIConnector(OutputConnector):
    def __init__(self, api=None):
        self.cc = api
    
    def write(self,data):
        logging.info("[CoachCareAPIConnector] Posting Body Measurement to Coachcare API")
        logging.debug("[CoachCareAPIConnector] data: \n{}\n".format(json.dumps(data, indent=2)))
        result = self.cc.post_body_measurement(**data)
        if not result:
            logging.error("[CoachCareAPIConnector] UnSucessful post to Coachcare API")
        logging.debug("[CoachCareAPIConnector] api results: " + str(result))
        return result
