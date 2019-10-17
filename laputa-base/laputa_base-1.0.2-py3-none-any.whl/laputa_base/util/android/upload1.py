import requests
import os
import json
from requests_toolbelt.multipart.encoder import MultipartEncoder

from src.util.android.operation_json import OperationJson
from src.util.android.cmd import Cmd

def upload(system, module, version, result, file):
    """
    :param system: 'Android', 'iOS'
    :param module: '功能', '兼容'
    :param version:
    :param result:  内容：result = {'duration': 0, 'result': [json文件中结果列表], 'device': []}
    :param file: html.zip的路径  log放到html中后再打包
    :return:
    """
    report_path=os.path.split(file)[0]
    if os.getenv('up_env') == '测试':
        host='https://do-kunlun-manager-qa.nioint.com'
        front_url='https://kunlun-front-qa.nioint.com/reporter'
    else:
        host='https://kunlun-manager.nioint.com'
        front_url = 'https://kunlun.nevint.com/reporter'
    if system not in ['Android', 'iOS']:
        raise ValueError('system参数错误，限制参数范围：Android、iOS')
    if module not in ['功能', '兼容']:
        raise ValueError('module参数错误，限制参数范围：功能、兼容')
    url = host+'/reporter/uploadReport'
    fail_count=0
    pass_count=0
    skip_count=0
    for v in result['result'].values():
        if v['result']=='Fail' or v['result']=='Error':
            fail_count+=1
        elif v['result']=='Pass':
            pass_count+=1
        elif v['result']=='Skipped':
            skip_count+=1
    data = {
        "product": "APP集成",
        "system": system,
        "module": module,
        "version": version,
        "testEnv": "STG",
        "duration": result['duration'],
        "success": True if len(result['result']) == pass_count else False,
        "caseCount": len(result['result']),
        "caseSuccessCount": pass_count,
        "caseFailCount": fail_count,
        "caseSkipConut": skip_count,
        "deviceId": result['device'],
        "buildLink": "http://jenkins.nevint.com/job/DD_nio-app-int-laputa-%s/%s/console"
                     % ('android' if system in ['Android','android'] else 'ios', os.getenv('BUILD_NUMBER')),
    }
    m = MultipartEncoder(
        fields={
            'file': ('%s.zip' % os.getenv('BUILD_NUMBER'), open(file, 'rb'), 'application/zip'),
            'data': json.dumps(data)
        }
    )
    headers = dict()
    headers['Content-Type'] = m.content_type
    headers['boundary'] = '----WebKitFormBoundary7MA4YWxkTrZu0gW'
    for i in range(5):
        try:
            respone = requests.post(url, data=m, headers=headers,timeout=600)
            respone_text = respone.text
            path = respone.json()['data']['reportFile']
            url = host+'/reports' + path + '/index.html'
            with open(os.getenv('WORKSPACE') + '/laputa_env', 'w') as f:
                f.write('report_url=' + url+'\n')
                f.write('front='+front_url)
            os.system('sudo rm -rf {0}/html'.format(report_path))
            os.system('sudo rm -rf {0}'.format(file))
            return
        except:
            if i== 4:
                print('报告上传失败,接口内容', respone_text)
                show_path = '/var/www/html/laputa_report/android/%s' % os.getenv('BUILD_NUMBER')
                os.system('sudo cp -a %s %s' % (report_path, show_path))
                with open(os.getenv('WORKSPACE') + '/laputa_env', 'w') as f:
                    f.write('report_url=http://10.143.16.21/laputa_report/android/'
                            '{}/html'.format(os.getenv('BUILD_NUMBER')))
                    f.write('front='+front_url)
                os.system('sudo rm -rf {0}/html'.format(report_path))
                os.system('sudo rm -rf {0}'.format(file))

if __name__ == '__main__':
    os.environ['BUILD_NUM']='1'
    os.environ['WORKSPACE']=os.path.abspath(os.path.join(os.path.dirname(__file__),'../../..'))
    devices=Cmd().get_devices()
    for device in devices:
        file='../../test_report/result/case_result_%s.json'% device
        oj=OperationJson(file=file)
        data=oj.read_json()
        result={'duration':100,'result':data[device],'device':device}
        print(result)
        upload('Android',module='功能',version='3.9.7',result=result,
         file='../../test_case/html.zip')
