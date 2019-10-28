from atp import requests_utils, logger

ATP_GLOBAL_DATA_URL = "http://internal-atp-1542801509.us-east-1.elb.amazonaws.com/globalData/"

logger.setup_logger("debug")


def get_global_data_by_env(env, default_atp_url=ATP_GLOBAL_DATA_URL):
    logger.log_info("get atp global data by env : %s" % env)
    res = requests_utils.get(default_atp_url + env)
    env_global_data_info = res.json()
    return env_global_data_info
