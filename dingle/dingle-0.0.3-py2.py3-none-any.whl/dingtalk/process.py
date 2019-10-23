# -*- coding: utf-8 -*-
'''
Manage dingtalk work flow process.
Document available at
https://ding-doc.dingtalk.com/doc#/serverapi2/ca8r99
and
https://ding-doc.dingtalk.com/doc#/serverapi2/civf9v
'''
import time
from ..util.api import check_none_params, client
from ..util.conf import get_config
from .models import convert_to_dict,\
                    FormComponent,\
                    FormComponentProp,\
                    ProcessInstanceApprover


def process_save(agent_id=None,
                 process_code=None,
                 name='',
                 description='',
                 form_component_list=None):
    if agent_id is None:
        agent_id = get_config().get('agent_id')
    request = {
        "agentid": agent_id,
        "process_code": process_code,
        "name": name,
        "description": description,
        "fake_mode": True
    }
    request['form_component_list'] = convert_to_dict(form_component_list)
    resp = client.call('POST', '/topapi/process/save',
                       json={"saveProcessRequest": request})
    return resp.json()


def process_delete(agent_id=None,
                   process_code=None):
    if not process_code:
        raise Exception("Must provide a process_code.")
    if agent_id is None:
        agent_id = get_config().get('agent_id')
    data = {
        "agentid": agent_id,
        "process_code": process_code
    }
    resp = client.call('POST', '/topapi/process/delete',
                       json=data)
    return resp.json()


def process_workrecord_create(agent_id=None,
                              process_code=None,
                              originator_user_id=None,
                              title=None,
                              form_component_values=None,
                              url=None):
    if not (process_code and originator_user_id and url):
        raise Exception("Must provide a process_code.")
    if agent_id is None:
        agent_id = get_config().get('agent_id')
    request = {
        "agentid": agent_id,
        "process_code": process_code,
        "originator_user_id": originator_user_id,
        "title": title,
        "form_component_values": form_component_values,
        "url": url
    }
    resp = client.call('POST', '/topapi/process/workrecord/create',
                       json={"request": request})
    return resp.json()


def process_workrecord_update(agent_id=None,
                              process_instance_id=None,
                              status=None,
                              result=None):
    if not (process_instance_id and status):
        raise Exception("Must provide a process_instance_id and status.")
    if not status in ('COMPLETED', 'TERMINATED'):
        raise Exception("Illegal status.")
    if agent_id is None:
        agent_id = get_config().get('agent_id')
    request = {
        "agentid": agent_id,
        "process_instance_id": process_instance_id,
        "status": status,
        "result": result
    }
    resp = client.call('POST', '/topapi/process/workrecord/update',
                       json={"request": request})
    return resp.json()


def process_workrecord_task_create(agent_id=None,
                                   process_instance_id=None,
                                   activity_id=None,
                                   tasks=None):
    if not (process_instance_id and status):
        raise Exception("Must provide a process_instance_id and status.")
    if agent_id is None:
        agent_id = get_config().get('agent_id')
    if tasks is None:
        tasks = []
    request = {
        "agentid": agent_id,
        "process_instance_id": process_instance_id,
        "activity_id": activity_id,
        "tasks": tasks
    }
    resp = client.call('POST', '/topapi/process/workrecord/task/create',
                       json={"request": request})
    return resp.json()


def process_workrecord_task_update(agent_id=None,
                                   process_instance_id=None,
                                   tasks=None):
    if not process_instance_id:
        raise Exception("Must provide the process_instance_id.")
    if agent_id is None:
        agent_id = get_config().get('agent_id')
    request = {
        "agentid": agent_id,
        "process_instance_id": process_instance_id,
        "tasks": tasks
    }
    resp = client.call('POST', '/topapi/process/workrecord/task/update',
                       json={"request": request})
    return resp.json()
 

def process_workrecord_taskgroup_cancel(agent_id=None,
                                        process_instance_id=None,
                                        activity_id=None):
    if not (process_instance_id and activity_id):
        raise Exception("Must provide the process_instance_id and activity_id.")
    if agent_id is None:
        agent_id = get_config().get('agent_id')
    request = {
        "agentid": agent_id,
        "process_instance_id": process_instance_id,
        "activity_id": activity_id
    }
    resp = client.call('POST', '/topapi/process/workrecord/taskgroup/cancel',
                       json={"request": request})
    return resp.json()


def processinstance_create(agent_id=None,
                           process_code=None,
                           originator_user_id=None,
                           dept_id=None,
                           approvers=None,
                           approvers_v2=None,
                           cc_list=None,
                           cc_position=None,
                           form_component_values=None):
    check_none_params(process_code=process_code,
                      originator_user_id=originator_user_id,
                      dept_id=dept_id,
                      form_component_values=form_component_values)
    if agent_id is None:
        agent_id = get_config().get('agent_id')
    data = {
        'agent_id': agent_id,
        'process_code': process_code,
        'originator_user_id': originator_user_id,
        'dept_id': dept_id,
        'approvers': approvers,
        'approvers_v2': convert_to_dict(approvers_v2),
        'cc_list': cc_list,
        'cc_position': cc_position,
        'form_component_values': convert_to_dict(form_component_values)
    }
    resp = client.call('POST', '/topapi/processinstance/create',
                       json=data)
    return resp.json()


def processinstnce_listids(process_code=None,
                           start_time=None,
                           end_time=None,
                           size=20,
                           cursor=0,
                           userid_list=None):
    check_none_params(process_code=process_code,
                      start_time=start_time)
    data = {
        "process_code": process_code,
        "start_time": start_time,
        "end_time": end_time,
        "size": size,
        "cursor": cursor,
        "userid_list": userid_list
    }
    resp = client.call('POST',
                       '/topapi/processinstance/listids',
                       json=data)
    return resp.json()


def processinstance_get(process_instance_id):
    resp = client.call('POST', '/topapi/processinstance/get',
                       json={'process_instance_id': process_instance_id})
    return resp.json()


def process_gettodonum(userid):
    data = {"userid": userid}
    resp = client.call('POST',
                       '/topapi/process/gettodonum',
                       json=data)
    return resp.json()


def process_listbyuserid(userid=None,
                         offset=0,
                         size=100):
    check_none_params(userid=userid)
    data = {
        "userid": userid,
        "offset": offset,
        "size": size
    }
    resp = client.call('POST',
                       '/topapi/process/listbyuserid',
                       json=data)
    return resp.json()


def processinstance_cspace_info(user_id=None):
    check_none_params(user_id=user_id)
    data = {'user_id': user_id}
    resp = client.call('POST', '/topapi/processinstance/cspace/info',
                       json=data)
    return resp.json()
