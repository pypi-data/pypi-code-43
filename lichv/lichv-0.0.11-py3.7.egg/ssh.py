import pymysql
from sshtunnel import open_tunnel

class mysqlConnectBySSH(object):
    ssh_host=''
    ssh_port=''
    ssh_user=''
    ssh_password=''

    mysql_host=''
    mysql_port=''
    mysql_user=''
    mysql_passwd=''
    mysql_db=''
    """docstring for mysqlConnectBySSH"""
    def __init__(self):
        pass

    def setSSH(self,host,port,user,passwd):
        self.ssh_host = host
        self.ssh_port = port
        self.ssh_user = user
        self.ssh_passwd = passwd
        return self

    def setConnect(self,host,port,user,passwd,db):
        self.mysql_host = host
        self.mysql_port = port
        self.mysql_user = user
        self.mysql_passwd = passwd
        self.mysql_db = db
        return self

    def query(self,sql):
        result = None
        with open_tunnel( (self.ssh_host, self.ssh_port), ssh_username=self.ssh_user, ssh_password=self.ssh_passwd, remote_bind_address=(self.mysql_host, self.mysql_port), local_bind_address=('0.0.0.0', 10022) ) as server:
            connect = pymysql.connect( host='127.0.0.1', port=10022, user=self.mysql_user, passwd=self.mysql_passwd, database=self.mysql_db)
            if connect:
                cursor = connect.cursor()
                cursor.execute(sql.encode('utf8'))
                result = cursor.fetchone()
                connect.commit()
                cursor.close()
                connect.close()
        return result

    def queryMany(self,sql):
        result = None
        with open_tunnel( (self.ssh_host, self.ssh_port), ssh_username=self.ssh_user, ssh_password=self.ssh_passwd, remote_bind_address=(self.mysql_host, self.mysql_port), local_bind_address=('0.0.0.0', 10022) ) as server:
            connect = pymysql.connect( host='127.0.0.1', port=10022, user=self.mysql_user, passwd=self.mysql_passwd, database=self.mysql_db)
            if connect:
                cursor = connect.cursor()
                cursor.execute(sql.encode('utf8'))
                result = cursor.fetchall()
                connect.commit()
                cursor.close()
                connect.close()
        return result

    def execute(self,sql,type='exec'):
        result = None
        with open_tunnel( (self.ssh_host, self.ssh_port), ssh_username=self.ssh_user, ssh_password=self.ssh_passwd, remote_bind_address=(self.mysql_host, self.mysql_port), local_bind_address=('0.0.0.0', 10022) ) as server:
            connect = pymysql.connect( host='127.0.0.1', port=10022, user=self.mysql_user, passwd=self.mysql_passwd, database=self.mysql_db)
            if connect:
                cursor = connect.cursor()
                result = cursor.execute(sql.encode('utf8'))
                connect.commit()
                cursor.close()
                connect.close()
        return result


if __name__ == "__main__":
    sql = "SELECT count(1) as `count` FROM `member`;"
    SelectResult = mysqlConnectBySSH().setSSH('0.0.01',11022,'admin','11111').setConnect('127.0.0.1',3306,'root','1111111','data').query(sql)
    print(SelectResult)
    print('FINISH!')