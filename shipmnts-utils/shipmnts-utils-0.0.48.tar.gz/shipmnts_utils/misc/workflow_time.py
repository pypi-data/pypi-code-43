import time
from shipmnts_utils.sql_executor import execute_select_query
from shipmnts_utils.redis_init import RedisConfig

redis = RedisConfig()
redis_client = redis.client

def calculate_workflow_time(job_id):
    auto_flow_time_spent, rerun_flow_time_spent = "0", "0"
    auto_flow_start = fetch_time("auto_flow", job_id)
    rerun_auto_flow_start = fetch_time("rerun_flow", job_id)
    end_time = float(time.time())
    if auto_flow_start:
        start_time = float(auto_flow_start)
        auto_flow_time_spent = str(round(end_time - start_time, 4))
    if rerun_auto_flow_start:
        rerun_start_time = float(rerun_auto_flow_start)
        rerun_flow_time_spent = str(round(end_time - rerun_start_time, 4))
    return [auto_flow_time_spent, rerun_flow_time_spent]


def fetch_time(prefix, job_id):
    return redis_client.get("{0}_{1}".format(prefix, job_id))
