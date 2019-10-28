import os 
import dotenv

COMMON_PATH = os.path.dirname(os.path.abspath(__file__))
ROOT_PATH = "/".join(COMMON_PATH.split("/")[:-1])
SHARED_PATH = ROOT_PATH + "/share"
ENV_FILE_PATH = SHARED_PATH + "/worker.env"

ENVS = dotenv.dotenv_values(ROOT_PATH + "/env.development")
TRACKER_ADDR = ENVS["TRACKER_ADDR"]
IMAGE = ENVS["IMAGE"]
VERSION = ENVS["VERSION"]