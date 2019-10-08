#!/usr/bin/env python
# -*- coding=utf-8 -*-


import sys
from arguments import Arguments
from formatter import Formatter
from shellCommand import Shell
from result import Result



class GitTool(object):

    __instance = None

    def __init__(self):
        # self.__load_config()
        self.arguments = Arguments.instance()
        self.formatter = Formatter.instance()
        self.shell = Shell.instance()
        self.result = Result.instance()

    @classmethod
    def instance(cls):
        if cls.__instance is None:
            cls.__instance = GitTool()
        return cls.__instance

    def _git(self, cmd, projectPath=""):
        if not projectPath:
            projectPath = self.arguments.projectPath
        projectGitPath = projectPath + "/.git"
        cmd = "git --work-tree=" + projectPath + " --git-dir=" + projectGitPath + " " + cmd
        self.formatter.format_print(cmd)
        returnCode, content = self.shell.excommand_until_done(cmd)
        if returnCode > 0:
            self.result.returnError("执行命令失败："+ cmd)
        return (returnCode, content)

    def clean(self, projectPath=""):
        self._git("add .", projectPath)
        if self.arguments.debug:
            return self._git("reset --soft HEAD~1", projectPath)
        else:
            return self._git("reset --hard", projectPath)

    def pull(self, projectPath=""):
        return self._git("pull", projectPath)

    def push(self, projectPath=""):
        return self._git("push origin ", projectPath)

    def commit(self, message, projectPath=""):
        self._git("add .", projectPath)
        return self._git("commit -m \"" + message + "\"", projectPath)

    def realBranchs(self, commitId):
        returnCode, content = self._git("branch -r --contains " + commitId)
        if returnCode > 0:
            self.result.returnError(" 请确认commtid是否正确")
        branchs = content.strip("\n").split("\n")
        branchList = []
        for branch in branchs:
            if "-> origin/master" in branch:
                continue
            branch = str(branch).strip("\n").strip(" ").replace("origin/", "")
            branchList.append(branch)
        return branchList

    def currentBranchAndCommitID(self):
        # 判断branch和commit
        commitId = self.arguments.commitId
        branch = self.arguments.branch
        projectPath = self.arguments.projectPath
        if commitId:
            realBranchList = self.gitTool.realBranchs(commitId)
            if branch and branch not in realBranchList:
                self.result.returnError("commit 所在分支并非提供的分支" + branch + "，而是在" + str(realBranchList))
            if not branch:
                if realBranchList and len(realBranchList) == 1:
                    realBranch = realBranchList[0]
                    self.formatter.format_info("即将用在commitID" + commitId + "所在的分支" + realBranch + "进行打包")
                    branch = realBranch
                else:
                    self.result.returnError("提供的commitID在如下的branch里：" + str(realBranchList) + ",请用--branch指定一个")
        else:
            if not branch:
                self.result.returnError("commitID 或者 branch 至少提供一种")
            else:
                self.formatter.format_info("即将用在分支" + branch + "上用最新的commit进行打包")
                count = self.unPushedCount()
                if count == 0:
                    cmd = "rev-parse " + branch
                else:
                    cmd = "rev-parse " + branch + "~" + str(count)
                returnCode, newCommitId = self._git(cmd, projectPath)
                if returnCode > 0:
                    self.result.returnError("不能获取当前分支的最新commit")
                commitId = str(newCommitId).strip("\n")
        return (branch, commitId)

    def unPushedCount(self, projectPath=""):
        returnCode, content = self._git("cherry", projectPath)
        count = 0
        if content:
            count = len(content.strip("").strip("\n").split("\n"))
        return count

    def checkout(self, branch, projectPath=""):
        return self._git("checkout " + branch, projectPath)

    def tag(self):
        return self._git("tag ")
