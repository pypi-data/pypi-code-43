#!/usr/bin/python
# -*- coding: UTF-8 -*-
# 主要公用方法

import datetime
import json
import time
import os
import random
import string
from autox import constants as cs
from autox.core import myemail as email, myrequest as request
import autox.core.mydb as database
from autox.model import model as mm
import autox.model.report as mr
import autox.util.others as others
import re

from autox.core.myresponse import getRelyValues
import traceback
import autox.core.mylog as log

logging = log.track_log()

summary_report = []
single_start = datetime.datetime.now()
single_end = datetime.datetime.now()
result = None
collect_data = {}
pass_result = 0
fail_result = 0
skip_result = 0
dict_list = []
case_result = []
case_names = []
scenarios = []
case_all_count = 0


class MyRegression:

    excReport = mr.Report()
    getRelyValues = getRelyValues()

    def __init__(self):
        pass

    def prepare_data(self, host, user, password, db, sql):
        # database.connect(host, user, password, db)
        d_result = database.execute(host, user, password, db, sql)
        # database.close()
        return d_result

    def execute_case(self, sql1, sql2):
        """
        :param filename: 用例文件名称
        :return: 测试结果的报告模板

        """
        global summary_report, result, pass_result, fail_result, skip_result, case_all_count
        host = cs.DB_HOST
        user = cs.DB_USER
        password = cs.DB_PASSWORD
        db = cs.DB_NAME
        sql_case = sql1
        sql_scenario = sql2
        report_title = cs.TEST_REPORT_TITLE

        """
        准备连接数据库获得用例
        执行完SQL，记得关闭数据库连接
        """
        con = database.connect(host, user, password, db)

        case_scenario = database.execute(con, sql_scenario)
        for sc in range(len(case_scenario)):
            scenario_name = (case_scenario[sc]['scenario_name'])

        case_lists = database.execute(con, sql_case)
        for ci in range(len(case_lists)):
            case_result.append(eval(case_lists[ci]['case_info']))
        for cn in range(len(case_result)):
            case_names.append(case_result[cn]['caseName'])

        database.close(con)

        # case_names = rc.get_casename(filename)[0]
        # case_lists = rc.get_casename(filename)[1]

        all_result = len(case_names)
        case_all_count = all_result + case_all_count
        total_start = others.get_now()[0]
        project_name = "企业测试项目" + ''.join(random.sample(string.ascii_letters + string.digits, 3))
        delivery_time = str(others.get_future(60))


        try:
            for i in range(0, all_result):
                case_list = case_result[i]
                name = case_names[i]
                method = case_list['caseMethod']
                request_data = case_list['request']
                expect_body = case_list['assertions']['body']
                expect_code = expect_body['code']
                expect_assert = None
                if len(expect_body) == 2:
                    expect_assert = expect_body['assert']
                assert_len = 0
                if case_list['caseName'] == '发布企业项目':
                    case_list['request']['body']['projectName'] = project_name
                if case_list['caseName'] == '发布企业项目':
                    case_list['request']['body']['deliveryTime'] = delivery_time
                if case_list['caseName'] == '提交确认函':
                    case_list['request']['body']['projectName'] = project_name + '子项目'
                str_data = str(case_list)
                if len(collect_data) > 0:
                    match_object = re.findall('.*?([\u4E00-\u9FA5]+\.[\d]\.[\\w]+)', str_data)
                    expect_assert_name = str(expect_assert).split(":")[0]
                    if expect_assert_name in match_object:
                        match_object.remove(expect_assert_name)
                    if len(match_object) == 0:
                        pass
                    else:
                        for i in match_object:
                            collect_response = collect_data[i.split('.')[0]]
                            res_code = getRelyValues.get_dict_value(getRelyValues, collect_response, 'code', 1, dict_list)
                            if int(res_code) > 0:
                                continue

                            value_index = i.split('.')[1]
                            actual_value = i.split('.')[2]
                            replace_value = getRelyValues.get_dict_value(getRelyValues, collect_response, actual_value,
                                                                         int(value_index), dict_list)

                            str_data = str_data.replace(i, str(replace_value))
                            data_json = eval(str_data)
                            headers = data_json['request']['headers']
                            api_url = data_json['caseUrl']
                            url = cs.BASEURL + api_url
                            _data = data_json['request']['body']
                data_json = eval(str_data)
                headers = data_json['request']['headers']
                api_url = data_json['caseUrl']
                url = cs.BASEURL + api_url
                _data = data_json['request']['body']
                data = json.dumps(_data, indent=4, sort_keys=False, ensure_ascii=False)
                data = data.encode('utf-8')
                if 'caseSleep' in data_json:
                    sleep_time = data_json['caseSleep']
                    actual_response = request.get_message(method, url, data, headers)
                    time.sleep(sleep_time)
                else:
                    actual_response = request.get_message(method, url, data, headers)
                collect_data[name] = actual_response
                res_str = ""
                if expect_assert is not None:
                    assert_object = re.findall('.*?([\u4E00-\u9FA5]+\.[\d]\.[\\w]+)', expect_assert)
                    for k in assert_object:
                        res_str = k.split('.')[2]
                        res_str_index = k.split('.')[1]
                        assert_replace_value = getRelyValues.get_dict_value(getRelyValues, actual_response, res_str,
                                                                            res_str_index, dict_list)
                        k = expect_assert.replace(k, str(assert_replace_value))
                        assert_list = k.split(":")
                        assert_len = len(set(assert_list))

                try:
                    if actual_response is not None:
                        if 'status_result' in actual_response:
                            actual_code = actual_response['status_result'][0]
                            if actual_code == -1 or -3:
                                actual_status_code = actual_response['status_code']
                            elif actual_code == 1:
                                actual_status_code = actual_code
                            else:
                                actual_status_code = None
                        else:
                            actual_code = actual_response['code']
                            actual_status_code = None

                        if actual_status_code is not None:
                            logging.info("回归测试失败:%s" % name)
                            test_status = "失败"
                            fail_result = fail_result + 1
                            request_log_message = "输入值: %s\n" % request_data

                        elif actual_code == expect_code and expect_assert is None:
                            logging.info("回归测试通过:%s" % name)
                            test_status = "成功"
                            pass_result = pass_result + 1
                            request_log_message = "输入值: %s\n" % request_data

                        elif assert_len == 1:
                            logging.info("回归测试通过:%s" % name)
                            test_status = "成功"
                            pass_result = pass_result + 1
                            request_log_message = "输入值: %s\n" % request_data

                        else:
                            logging.info("回归测试失败:%s" % name)
                            test_status = "失败"
                            fail_result = fail_result + 1
                            if assert_len > 1:
                                actual_result = res_str + "预期结果:%s\n" % assert_list[1] + " 实际结果:%s\n" % assert_list[0]
                                request_log_message = "输入值: %s\n" % request_data
                                result_log_message = "输出结果: 预判值错误, %s\n" % actual_result
                                run_time = str(actual_response['run_time']) + 'ms'
                                summary_report = self.excReport.sum_result(caseScenario, url, method, name, run_time,
                                                                           test_status, request_log_message,
                                                                           result_log_message)
                                continue
                            else:
                                request_log_message = "输入值: %s\n" % request_data

                except Exception as e:
                    logging.error("无返回结果%s" % e)
                    traceback.print_exc(file=open(os.getcwd()+'/log/error.log', 'a+'))
                run_time = str(actual_response['run_time']) + 'ms'
                # del actual_response['run_time']
                result_log_message = "输出结果:%s\n" % actual_response
                if len(url) > 120:
                    url = url[0:110]
                summary_report = self.excReport.sum_result(scenario_name, url, method, name, run_time, test_status,
                                                           request_log_message, result_log_message)

        except Exception as e:
            logging.error(e)
            traceback.print_exc(file=open(os.getcwd()+'/log/error.log', 'a+'))

        total_end = others.get_now()[0]
        total_run_time = str(others.get_mills(total_start, total_end)) + 's'

        skip_result = case_all_count - pass_result - fail_result
        report_model = mm.ReportModel(summary_report, report_title, case_all_count, pass_result,
                                      fail_result, skip_result, total_run_time)

        return report_model

    def build_report(self, scenario):
        try:
            scenario = '%' + scenario + '%'
            sql1 = "select case_info from t_case where id in (select case_id from t_matching where scenario_id in " \
                  "(select id from t_scenario where scenario_name like '%s'))" %scenario
            sql2 = "select scenario_name from t_scenario where scenario_name like '%s'" %scenario
            test_report = self.execute_case(sql1, sql2)
            return self.excReport.build_report(test_report.sum_report, test_report.name, test_report.all_test,
                                               test_report.pass_test, test_report.fail_test, test_report.skip_test,
                                               test_report.total_run_time)
        except Exception as e:
            logging.error(e)
            traceback.print_exc(file=open(os.getcwd()+'/log/error.log', 'a+'))

    def send_email(self, reportfile):
        reports = os.listdir(reportfile)
        reports.sort(key=lambda fn: os.path.getatime(reportfile + '/' + fn))
        file = os.path.join(reportfile, reports[-1])
        email.email(file)
