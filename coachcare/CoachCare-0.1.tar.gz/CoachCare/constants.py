import logging
import os, sys
from pathlib import Path
from datetime import datetime
import json
import shutil


#//// Listener service Constants ///////
HOST = '127.0.0.1'
PORT = '9999'

#//// Log Configs /////////////
SECA_LOG_DIR = "C:\\ProgramData\\seca\\LogFiles\\"
LOG_FILE = SECA_LOG_DIR + "Seca.CoachCare." + datetime.now().strftime("%Y%m%d") + ".log"
formatter = logging.Formatter('%(levelname)s:[%(name)s]: %(message)s')
logging.basicConfig(filename=LOG_FILE,level=logging.DEBUG, format='%(levelname)s:[%(name)s]: %(message)s')
#console = logging.StreamHandler()
#console.setLevel(logging.DEBUG)
#console.setFormatter(formatter)
#logger = logging.getLogger('')
#logger.addHandler(console)

#// Flask logger
flask_log = logging.getLogger('werkzeug')
flask_log.setLevel(logging.FATAL)
flask_log.disabled = True
#flask_log.setLevel(logging.DEBUG)
#flask_log.disabled = False

#//// CoachCare API Constants ////////////
API_VERSION = '2.0'
WEBHOOK_API_VERSION = '1.0'
AUTH_VERSION = '2.0'

#//////////// URL coachcaredev 
BASE_URL = 'https://api.coachcaredev.com/'

#BASE_URL = 'https://api.coachcare.com/'


URL = BASE_URL + API_VERSION
AUTH_URL = BASE_URL + AUTH_VERSION

#BASE_HEADER = {'Accept':'application/json',
#               'Content-Type':'application/x-www-form-urlencoded'}

BASE_HEADER = {
               'Content-Type':'application/json'
               }
GET_HEADER = {'Authorization':""}

#//// Common Global Constants //////////////
BASE_DIR = str(Path(os.path.dirname(__file__))) + "\\"
LISTENER_OUTPUT_DIR = BASE_DIR + "restservice\\listenerRecieved\\"
CONFIG_DIR = BASE_DIR + "configs\\"
ex_config_dir = "coachcare_config"
EXTERNAL_CONFIG_DIR = os.path.join("C:\\", ex_config_dir) + "\\"
EMR_CONNECT_INPUT_DIR = "C:\\KisToSecaSuc\\" #accepts ADT message
EMR_CONNECT_OUTPUT_DIR = "C:\\SecaSucToKis\\" #outputs ORU message
INTERNAL_TEMPLATE_DIR = BASE_DIR + "Templates\\"
TEST_DATA_DIR = BASE_DIR + "tests\\test_data\\"


#Create External Config Dir if it doesn't exist
if not os.path.isdir(EXTERNAL_CONFIG_DIR):
    for i in range(5):
        try:
            os.makedirs(EXTERNAL_CONFIG_DIR) 
            break
        except: pass

#//// Test DIRS /////////////
EXAMPLE_ORU_DIR = BASE_DIR + "tests\\test_data\\ExampleMessages\\ORU\\"
EXAMPLE_ADT_DIR = BASE_DIR + "tests\\test_data\\ExampleMessages\\ADT\\"
EXAMPLE_JSON_DIR = BASE_DIR + "tests\\test_data\\ExampleMessages\\JSON\\"
EXAMPLE_TEMPLATE_DIR = BASE_DIR + "tests\\test_data\\"
FILE_WATCHER_DIR = BASE_DIR + "tests\\test_data\\file_watcher_test_dir"

#//// PyInstaller Vars ///////////////
#These variables are set by pyInstaller if running from a frozen(static) build
is_frozen = getattr(sys, 'frozen', False)
frozen_temp_path = getattr(sys, '_MEIPASS', '')

