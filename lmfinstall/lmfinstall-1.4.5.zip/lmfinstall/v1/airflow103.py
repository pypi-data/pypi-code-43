from fabric import Connection

from invoke import Responder


from lmfinstall.v1 import python 



#


def install(conp,python_file):
    #conp=["root@172.16.0.13:22","Since2015!"]
    python.install(conp,python_file)
    c=Connection(conp[0],connect_kwargs={"password":conp[1]})

    c.run("/opt/python35/bin/python3 --version")
    c.run("/opt/python35/bin/python3 -m pip install apache-airflow==1.10.3 psycopg2-binary  redis celery -i https://pypi.douban.com/simple",pty=True)
    c.run("""echo  "export AIRFLOW_HOME=/opt/airflow"  >> /etc/profile  && source /etc/profile""",pty=True)
    c.run("""/opt/python35/bin/airflow   """,pty=True,warn=True)
    c.run("ip addr")

    c.run("useradd wk ",pty=True,warn=True)



#install(["root@172.16.0.13:22","Since2015!"],'')