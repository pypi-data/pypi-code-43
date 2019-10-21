import json
import os
import time
from arms.utils import exe, not_ready, assert_or_exit


def strip_end(url, suffix):
    return url[:-len(suffix)] if url.endswith(suffix) else url


def build_system():
    # gitlab-runner相关
    if not_ready("gitlab-runner"):
        assert exe('curl https://packages.gitlab.com/gpg.key 2> /dev/null | sudo apt-key add - &>/dev/null')
        with open('/etc/apt/sources.list.d/gitlab-runner.list', 'w') as fout:
            fout.write('deb https://mirrors.tuna.tsinghua.edu.cn/gitlab-runner/ubuntu xenial main\n')
        assert exe('sleep 3 && apt-get update')

    # docker相关
    if not_ready("docker"):
        assert exe('apt-get update')
        assert exe('apt-get install -y apt-transport-https ca-certificates curl software-properties-common')
        assert exe('curl -fsSL https://download.daocloud.io/docker/linux/ubuntu/gpg | sudo apt-key add -')
        assert exe('add-apt-repository "deb [arch=$(dpkg --print-architecture)] https://download.daocloud.io/docker/linux/ubuntu $(lsb_release -cs) stable"')
        assert exe('apt-get update')
        assert exe('apt-get install -y -q docker-ce')
        assert exe('service docker start')
        assert exe('docker ps')
        with open("/etc/docker/daemon.json", "w") as fout:
            fout.write(json.dumps({"registry-mirrors": ["http://11854a36.m.daocloud.io"]}))
        assert exe('service docker restart')
        time.sleep(2)

    # docker-compose相关
    if not_ready("docker-compose"):
        assert exe('curl -L https://get.daocloud.io/docker/compose/releases/download/1.24.1/docker-compose-`uname -s`-`uname -m` > /usr/local/bin/docker-compose')
        assert exe('chmod +x /usr/local/bin/docker-compose')

    # gitlab-runner相关
    if not_ready("gitlab-runner"):
        assert exe('apt-get install -y gitlab-runner')
        assert exe('usermod -a -G docker gitlab-runner')
        assert exe('mkdir -p /opt/docker_volumes && chown gitlab-runner /opt/docker_volumes')

    if os.system("docker network inspect common") != 0:
        assert exe('docker network create common')


def register_runner(domain):
    tag = strip_end(strip_end(strip_end(domain, '.cn'), '.com'), '.parsec')
    gitlab_url = input('Specify the following URL during the Runner setup: ')
    gitlab_token = input('Use the following registration token during setup: ')
    assert exe('gitlab-runner register -n --name {domain} --tag-list {tag} --executor shell --maximum-timeout 3600'
               ' -u {gitlab_url} -r {gitlab_token} '
               .format(domain=domain, tag=tag, gitlab_url=gitlab_url, gitlab_token=gitlab_token))
    assert exe('mv conf.d/http.example.com.cn.conf.disabled conf.d/{domain}.conf'.format(domain=domain))
    assert exe('arms run restart')