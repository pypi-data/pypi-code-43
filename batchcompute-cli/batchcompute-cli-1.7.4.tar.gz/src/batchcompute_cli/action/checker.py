from ..util import result_cache, oss_client, formater, client, dag,util,list2table
from terminal import white,green,red,magenta,bold,yellow,blue
import os
import datetime
from oss2.exceptions import NoSuchKey,NoSuchBucket
import json
from ..const import CMD,STRING
import re

SLEN = 60

def check(jobId):

    if jobId.startswith('-'):
        raise Exception('Invalid jobId')

    jobId = result_cache.get(jobId, 'jobs')

    print(white('exec: bcs check %s' %  jobId ))

    job = client.get_job(jobId)

    if job.Message:
        print('\n%s' % bold(red(job.Message)))

    task_items = formater.items2arr(client.list_tasks(jobId).get('Items'))


    ################
    desc = client.get_job_description(jobId)


    jobType = desc.get('Type')
    if jobType == 'DAG':
        # calc deps
        deps = util.get_task_deps(desc.get('DAG'))
        matric = dag.sortIndex(deps)

        # dag
        if len(task_items)>1:
            print('%s\n' % bold(magenta('DAG:')))
            dag.draw(deps, matric)

        task_items = util.sort_task_by_deps(task_items, matric)
        ############


    # print jobName
    print('\n%s' % bold(magenta('Tree:')))
    print('%s: %s (%s)' % (blue('JobName'), magenta(job.Name), formater.get_job_state(job.State)) )


    # task list

    for task in task_items:
        taskName = task.get('TaskName')
        taskState = task.get('State')

        print('  |- %s: %s (%s)' % (blue('TaskName'), magenta(taskName), formater.get_job_state(taskState)) )

        # instance list
        ins_items = formater.items2arr(client.list_instances(jobId, taskName).get('Items'))

        #hours = 0
        for ins in ins_items:
            instId = ins.get('InstanceId')
            instState = ins.get('State')

            print('    |- %s: %s (%s)' % (blue('InstanceId'), magenta(instId), formater.get_job_state(instState)) )

            # log
            #print_ins_log(jobId, taskName, ins)

            # result
            print_inst_result(jobId, taskName, ins)




    ins_map = {}
    ins_types = (client.list_instance_types() or [])
    for n in ins_types:
        ins_map[n.get('name')]=n
    spot_ins_types = (client.list_spot_instance_types() or [])
    for n in spot_ins_types:
        ins_map[n.get('name')] = n



    if desc.Type=='App' and desc.App.AppName==':cromwell':

        try:
            #print(desc.App.Outputs.get('OUTPUTS_DIR')+'workflow_metadata.json')
            jsonStr = oss_client.get_data(desc.App.Outputs.get('OUTPUTS_DIR')+'workflow_metadata.json')
            print('\n%s' % bold(magenta('BillingInfo(cromwell):')))
            meta = json.loads(jsonStr)


            coreHours = 0
            totalCoreHours = 0
            billingArr = []
            for (taskName, subJobs) in meta['calls'].items():
                totalHours= 0
                for item in subJobs:

                    hours = getHours(item['start'], item['end'])
                    totalHours += hours

                    cpu=0
                    if item['runtimeAttributes']['cluster']:
                       # cluster: Right(AutoClusterConfiguration(OnDemand,ecs.sn1.7xlarge,img-gatk4,None,None))
                       cpu = re.match(r'\w+\(\w+\(([\w,-.]+)\)\)', item['runtimeAttributes']['cluster']).group(1)
                       if cpu.find(',')!=-1:
                           cpu = ins_map[cpu.split(',')[1]]['cpu']
                       elif cpu.find(' ')!=-1:
                           cpu = ins_map[cpu.split(' ')[1]]['cpu']

                    elif item['runtimeAttributes']['instanceType']:
                       cpu = ins_map[item['runtimeAttributes']['instanceType']]['cpu']


                coreHours = totalHours * cpu
                totalCoreHours+= coreHours
                billingArr.append({'task': taskName,'count': len(subJobs), 'hours': totalHours,  'cpu': cpu, 'coreHours':coreHours})
            list2table.print_table(billingArr, ['task', 'count', 'cpu', 'hours', 'coreHours'])

            print('%s: %s' % (green('Total core * hours'), totalCoreHours))

        except Exception as ee:
            pass
            #print(ee)

    print(white('\n type "%s log <jobId|No.>" to show log detail\n' % CMD))


def getHours(start, end):
    if not start or not end:
        return 0
    if isinstance(start,STRING):
        start = datetime.datetime.strptime(start[0:-5],'%Y-%m-%dT%H:%M:%S%f')
        end = datetime.datetime.strptime(end[0:-5],'%Y-%m-%dT%H:%M:%S%f')

    return float((end - start).seconds)/3600


def print_inst_result(jobId, taskName, ins):
    result = ins.get('Result')
    instId = ins.get('InstanceId')

    if not result:
        return

    # print
    if result.get('ErrorCode'):
        print('       %s [%s:%s, %s:%s]' % (bold(('Result')), blue('TaskName'),magenta(taskName),blue('InstanceId'), magenta(instId) ))
        print(white('-'*SLEN))

        print(red(result))

        print(white('-'*SLEN))


