#!/usr/bin/env python
# -*- coding: utf-8 -*-
# AUTHOR: XYCoder
# FILE: /Users/v-sunweiwei/Desktop//xyscript/xyscript/ios/gitandjira.py
# DATE: 2019/08/16 Fri
# TIME: 17:33:35

# DESCRIPTION:gitlab相关操作与jira相关操作

import os,sys,re,json,datetime
from xyscript.common.xylog import *
from xyscript.common.mail import Email

LOGNUM = 10
LASTSUCCESS = None
CURRENTSUCCESS = None

class GitLab:
    def get_all_commit_between_push(self,code_branch,package_branch,workspace,mail,url=None,keyword=None):
        commit_result = {}
        os.chdir(workspace)
        commit_content = "merge " + code_branch + " into " + package_branch
        log_num = self.get_num_of_need_commit(commit_content,workspace)

        now = datetime.datetime.now()
        otherStyleTime = now.strftime("%Y-%m-%d %H:%M:%S")

        result = os.popen('git log -' + str(log_num) + ' --before="'+ otherStyleTime +'" --pretty=format:"%cn<%ce>%ce%cd%s" --date=iso')
        # print('git log -' + str(log_num) + ' --before="'+ otherStyleTime +'" --pretty=format:"%cn<%ce>%ce%cd%s" --date=iso')
        all_lines = result.readlines()
        all_commits = []
        for line in all_lines:
            info = line.split('')
            commit_info = {}
            commit_info['user'] = info[0]
            commit_info['date'] = info[2]
            commit_info['info'] = info[3].split('\n')[0]
            commit_info['email'] = info[1]
            all_commits.append(commit_info)
        
        last_commit_date = otherStyleTime
        # print(all_lines)
        old_commit_date = all_commits[-1]['date']
        cc = all_commits[0]['email']
        submodule_commit_list = []
        submodule_list = self._get_current_config_file()
        for moduleConfig in submodule_list:
            module_path = workspace + "/" + moduleConfig["module"]
            commit_array = self.get_submodule_changes_during(module_path,old_commit_date,last_commit_date)
            if len(commit_array) > 0:
                submodule_commit_list.append({'name':moduleConfig["module"],'commit_log':commit_array})

        
        public_module_list = []
        pod_path = workspace + '/' + 'Pods/'
        if os.path.exists(pod_path) and keyword is not None and len(keyword) >0:
            for root, dirs, files in os.walk(pod_path):
                for d in dirs:
                    if self._is_private_module(d,keyword):
                        commit_array = self.get_submodule_changes_during(module_path,old_commit_date,last_commit_date)
                        if len(commit_array) > 0:
                            public_module_list.append({'name':d,'commit_log':commit_array})
        
        commit_result['cc'] = cc
        commit_result['project_name'] = workspace.split('/')[-1]
        commit_result['start_time'] = last_commit_date
        commit_result['end_time'] = old_commit_date
        commit_result['code_branch'] = code_branch
        commit_result['package_branch'] = package_branch
        commit_result['shell'] = all_commits
        commit_result['submodule'] = submodule_commit_list
        commit_result['private_module'] = public_module_list
        if url is not None:
            commit_result['jiraurl'] = url
            
        Email([mail]).send_merge_result(commit_result)

    def _is_private_module(self,dir,keywords):
        for keyword in keywords:
            if dir.startswith(keyword):
                return True
        return False

    
    def get_submodule_changes_during(self,workspace,start_time,end_time):
        os.chdir(workspace)
        result = os.popen('git log --date=iso --before="'+ end_time +'" --after="' + start_time + '" --pretty=format:"%cn%cd%s"')
        all_lines = result.readlines()
        all_commits = []
        for line in all_lines:
            info = line.split('')
            commit_info = {}
            commit_info['user'] = info[0]
            commit_info['date'] = info[1]
            commit_info['info'] = info[2].split('\n')[0]
            all_commits.append(commit_info)
        return all_commits

    def _get_current_config_file(self):
        file = open("ProjConfig.json")
        moduleConfigList = json.load(file)
        return moduleConfigList
    
    def get_jira_url_with_commit(self,commit_info):
        pass

    def get_current_branch_name(self,workspace):
        os.chdir(workspace)
        result = os.popen('git branch')
        all_lines = result.readlines()
        for line in all_lines:
            if '* ' in line:
                return line[2:]
        return None

    def get_num_of_need_commit(self,content,workspace):
        global LOGNUM
        global LASTSUCCESS
        global CURRENTSUCCESS
        os.chdir(workspace)
        result = os.popen('git log -' + str(LOGNUM) + ' --pretty=format:"%cn<%ce>%cd%s"')
        all_lines = result.read()

        content_num = all_lines.count(content)

        # merge = re.compile('Merge\: ([a-z0-9]{7,})+([\t ]*)+([a-z0-9]{7,})')
        # merge_result = merge.findall(all_lines)
        # merge_num = len(merge_result)
        if content_num >=2:
            CURRENTSUCCESS = True
        else:
            CURRENTSUCCESS = False

        if LASTSUCCESS == True and CURRENTSUCCESS:
            LOGNUM = LOGNUM - 1
        elif LASTSUCCESS == False and CURRENTSUCCESS:
            return LOGNUM
        elif LASTSUCCESS == True and not CURRENTSUCCESS:
            return LOGNUM + 1
        elif LASTSUCCESS == False and not CURRENTSUCCESS:
            LOGNUM = LOGNUM + 1
        elif LASTSUCCESS is None and CURRENTSUCCESS:
            LOGNUM = LOGNUM - 1
        elif LASTSUCCESS is None and not CURRENTSUCCESS:
            LOGNUM = LOGNUM + 1

        LASTSUCCESS = CURRENTSUCCESS
        return self.get_num_of_need_commit(content,workspace)



if __name__ == "__main__":
    # 测试代码
    GitLab().get_all_commit_between_push(code_branch='Develop',package_branch='zuche-test',workspace='/Users/v-sunweiwei/Desktop//ios-shell-passenger',mail='m18221031340@163.com')
    # now = datetime.datetime.now()
    # print(now)
    # otherStyleTime = now.strftime("%Y-%m-%d %H:%M:%S")
    # print(otherStyleTime) 