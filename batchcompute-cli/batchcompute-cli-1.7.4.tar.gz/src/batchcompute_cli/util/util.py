
# -*- coding: UTF-8 -*-
import json
import os
from ..util import client,result_cache, config,oss_client
from terminal import yellow,blue
from ..const import CMD
import re
MOUNTS_PROTOCOLS = ['smb://','lustre://','nasplus://', 'nas://','oss://']

FALSE_ARR = ['', 'null', 'None', 'false', 'False','0']

def parse_id_arr(arr, type='jobs', needCheckGod=False):
    t=[]
    arr = _parse_shot_id(arr)

    for item in arr:
        id = result_cache.get(item, type, needCheckGod)
        t.append(id)
    return t

def _parse_shot_id(arr):
    t=[]
    for k in arr:
        if re.match(r"^\d+\-\d+$",k):
            (a,b) = k.split('-')
            t = t + range(int(a),int(b)+1)
        else:
            t.append(k)
    return t


# 检查是否在project目录下运行
def check_is_job_project():
    project_json_path = os.path.join(os.getcwd(),'project.json')
    job_json_path = os.path.join(os.getcwd(),'job.json')

    flag = os.path.exists( project_json_path ) and os.path.exists( job_json_path )
    if not flag:
        raise Exception('This is not a BatchCompute project folder')

    with open(project_json_path, 'r') as f:
        obj = json.loads(f.read())

    return obj.get('type')


def get_cluster_str(task_desc):
    if task_desc.get('ClusterId'):
        return task_desc.get('ClusterId')
    else:
        return "img=%s:type=%s" % (task_desc['AutoCluster']['ECSImageId'] or task_desc['AutoCluster']['ImageId'], task_desc['AutoCluster']['InstanceType'])


def parse_cluster_cfg(s=None, checkCluster=True):
    if not s:
        return {
            'AutoCluster':{
                'ImageId': config.get_default_image(),
                'InstanceType': config.get_default_instance_type()
            },
            'ClusterId': ''
        }

    if s.find('=')!=-1:
        arr = s.split(':')
        m={}
        for item in arr:
            if '=' not in item:
                raise Exception('Invalid cluster format')

            [k,v]=item.split('=',1)
            if k=='img':
                if v.startswith('img-') or v.startswith('m-'):
                    m['ImageId']=v
                # elif v.startswith('m-'):
                #     m['ECSImageId']=v
                else:
                    raise Exception('Invalid imageId: %s' % v)
            if k=='type':
                m['InstanceType']=v


        if not m.get('ImageId') and not m.get('ECSImageId'):
            m['ImageId']= config.get_default_image()

        if not m.get('InstanceType'):
            m['InstanceType']= config.get_default_instance_type()

        # if not it.get_ins_type_map().get(m['InstanceType']):
        #     print(yellow("Warning: '%s' may not be valid, type '%s it' for more" % (m['InstanceType'], CMD)))

        #print(white('using AuthCluster: %s' % m))
        return {'AutoCluster':m,'ClusterId':''}
    else:
        if checkCluster:
            result = client.list_clusters()
            clusters = result.get('Items')
            for c in clusters:
                if c.get('Id')==s:
                    #print(white('using Cluster: %s' % s))
                    return {'ClusterId':s,'AutoCluster':{}}

            raise Exception('Invalid ClusterId, type "%s c" for more' % CMD)
        else:
            return {'ClusterId': s, 'AutoCluster': {}}


def trans_mount_dup(s):
    if not s:
        return None
    arr = s.split(',')
    mounts = []
    m = {}
    for item in arr:
        item = item.strip()

        # :::
        if item.find(':::') != -1:
            arr = item.split(':::')
            k = arr[0]
            v = arr[1]
            w = arr[2] == 'true' if len(arr) == 3 else k.endswith('/')

            if v in MOUNTS_PROTOCOLS:
                (k,v) = (v,k)



        elif item.startswith('oss://') or item.startswith('nas://'):

            ind = item.rfind(':')

            k = item[0:ind]
            v = item[ind+1:]

            if v=='true' or v=='false':
                w = v=='true'
                ind2 = k.rfind(':')
                v = k[ind2 + 1:]
                k = k[0:ind2]
            else:
                w = k.endswith('/')
        else:
            if ':oss://' in item:
                ind = item.find(':oss://')
                v = item[0:ind]
                k = item[ind+1:]
                w = k.endswith('/')
            elif ':nas://' in item:
                ind = item.find(':nas://')
                v = item[0:ind]
                k = item[ind + 1:]
                w = k.endswith('/')

            else:
                raise Exception('Invalid mounts format')
                #[k,v]=item.split(':',1)

            if k.endswith(':true') or k.endswith(':false'):
                w = k.endswith(':true')
                k = k[:-6]


        if len(v)==1 and str.isalpha(v):
            v = v + ':'
        m[k+'^^^'+v] = {'Source':k, 'Destination': v, 'WriteSupport': w}

    for (k2,v2) in m.items():
        mounts.append(v2)
    return mounts


def trans_deps(deps):
    # A->b,c;d->e,f
    parts = deps.strip(';').split(';')
    m = {}
    for part in parts:
      if '->' in part:
        arr = part.split('->')
        count = len(arr)
        for i in range(count-1):
            k = arr[i]
            v = arr[i+1]

            ks = [x.strip() for x in k.split(',')]
            vs = [x.strip() for x in v.split(',')]
            for kn in ks:
                if not m.get(kn):
                    m[kn]=[]
                m[kn] += vs
            #m[k] = [x.strip() for x in v.split(',')]
    return m

def trans_mount(s):
    if not s:
        return None
    arr = s.split(',')
    mount = {}
    for item in arr:
        item = item.strip()
        if item.startswith('oss://') or item.startswith('nas://'):
            ind = item.rfind(':')
            k = item[0:ind]
            v = item[ind+1:]
        else:
            if ':oss://' in item:
                ind = item.find(':oss://')
                v = item[0:ind]
                k = item[ind+1:]
            elif ':nas://' in item:
                ind = item.find(':nas://')
                v = item[0:ind]
                k = item[ind + 1:]
            else:
                [k,v]=item.split(':',1)

        if len(v)==1 and str.isalpha(v):
            v = v + ':'
        mount[k]=v
    return mount


def trans_docker(docker=None, ignoreErr=False):
    if docker.startswith('registry'):
        return {"BATCH_COMPUTE_DOCKER_IMAGE": docker}
    
    ind = docker.find('@oss://')
    if ind > 1:

        [k,v]=docker.split('@oss://', 1)
        v = 'oss://%s' % v

        if not k.startswith('localhost:5000/'):
            k = 'localhost:5000/%s' % k
        return {"BATCH_COMPUTE_DOCKER_IMAGE":k, "BATCH_COMPUTE_DOCKER_REGISTRY_OSS_PATH":v}
    else:
        if not ignoreErr:
            raise Exception('Invalid docker option format')


def sort_task_by_deps(arr, matric):
    m = {}
    for n in arr:
        m[n['TaskName']]=n

    t=[]
    for items in matric:
        for taskname in items:
            t.append(m[taskname])
    return t


def get_task_deps(dag):
    deps = dag.get('Dependencies') or {}
    tasks = dag.get('Tasks')

    m = {}
    for k in tasks:
        m[k] = []

    for k in m:
        if not deps.get(k):
            deps[k] = []

    return deps

def print_inst_result(result):

    print('%s : %s' % (blue('ExitCode'), result.ExitCode))
    print('%s : %s' % (blue('ErrorCode'), result.ErrorCode))
    print('%s : %s' % (blue('ErrorMessage'), result.ErrorMessage))
    print('%s : %s' % (blue('Detail'), result.Detail))



def trans_disk(disk):

    try:
        infos = disk.split(',')

        result = {}

        for info in infos:
            info = info.strip()
            if info.startswith('system:'):
                (name, type, size) = info.split(':')
                type = type.strip()
                result['SystemDisk'] = {
                    'Type': '' if type=='default' else type, 'Size': int(size)
                }
            elif info.startswith('data:'):
                (name, type2, size2, mount_point) = info.split(':')
                type2 = type2.strip()
                result['DataDisk'] = {
                    'Type': '' if type2=='default' else type2, 'Size': int(size2), 'MountPoint': mount_point.strip()
                }
            else:
                raise Exception('Invalid disk format')

        return result

    except BaseException as e:
        raise Exception(
            'Invalid disk format, it should like this: --disk system:ephemeral:40,data:cloud:500:/home/disk, append -h for more')

def check_default_osspath(m):
    if not m.get('osspath'):
        print(yellow('\n  [WARN]: %s\n' % 'default osspath is recommended to set, use: "bcs set -o <osspath>'))
        return

    try:
        oss_client.list(m.get('osspath'))

    except Exception as e:
        print(yellow('\n  [WARN]: %s\n' % 'You need to change osspath too: bcs set -o <osspath>'))

def set_default_type_n_image():

    m = config.getConfigs(config.COMMON)

    # if not found default image
    default_image = m.get('defaultimage')
    if not default_image:
        m['defaultimage']='img-ubuntu'
        print(yellow('\n  [WARN]: defaultimage: %s' % m['defaultimage']))

    config.setConfigs(config.COMMON, m)


    default_type = m.get('defaulttype')
    if not default_type:
        print(yellow('\n  [WARN]: %s\n' % 'defaulttype is recommended to set, use: "bcs set -t <instance_type>", and type "bcs t" to see more'))


def check_default_vpc_cidr_block():

    m = config.getConfigs(config.COMMON)

    vpc_cidr_block = m.get('vpc_cidr_block')
    if not vpc_cidr_block:
        m['vpc_cidr_block'] = "192.168.0.0/16"
        print(yellow('\n  [WARN]: default vpc_cidr_block: %s' % m['vpc_cidr_block']))
        config.setConfigs(config.COMMON, m)
    