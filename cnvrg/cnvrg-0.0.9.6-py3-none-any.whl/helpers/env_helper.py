import os

EXPERIMENT = "Experiment"
ENDPOINT = "Endpoint"

ENV_KEYS = {
    "current_job_id": "CNVRG_JOB_ID",
    "current_job_type": "CNVRG_JOB_TYPE",
    "current_project": "CNVRG_PROJECT",
    "current_organization": "CNVRG_OWNER"
}

POOL_SIZE = os.environ.get("CNVRG_THREAD_SIZE") or 20
CURRENT_JOB_ID = os.environ.get("CNVRG_JOB_ID")
CURRENT_JOB_TYPE = os.environ.get("CNVRG_JOB_TYPE")
CNVRG_OUTPUT_DIR = os.environ.get("CNVRG_OUTPUT_DIR")
CURRENT_PROJECT_SLUG = os.environ.get(ENV_KEYS["current_project"])
CURRENT_ORGANIZATION_SLUG = os.environ.get(ENV_KEYS["current_organization"])
MAX_LOGS_PER_SEND = int(os.environ.get("CNVRG_MAX_LOGS_PER_SEND") or 500)

def in_experiment():
    return CURRENT_JOB_TYPE == EXPERIMENT


def get_origin_job():
    if not CURRENT_JOB_ID and not CURRENT_JOB_TYPE: return {}
    return {
        "origin_job_id": CURRENT_JOB_ID,
        "origin_job_type": CURRENT_JOB_TYPE
    }