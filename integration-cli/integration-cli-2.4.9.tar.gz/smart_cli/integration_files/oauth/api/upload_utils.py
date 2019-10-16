from integration_utils.tools import get_full_integrations
from event_monitoring import event


@event(keys=['integration_id', 'site_id'], list_value='task_list', iter_key='key')
def upload_data(task_list, key):
    pass