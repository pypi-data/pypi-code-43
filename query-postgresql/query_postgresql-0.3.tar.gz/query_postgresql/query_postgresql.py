import psycopg2
import pandas as pd

class query_postgresql:
    def __init__(self,hostname,username,password,database,port):
        self.hostname=hostname
        self.username=username
        self.password=password
        self.database=database
        self.port=port

    
    def query_todf(self,query):
        conn=psycopg2.connect(host=self.hostname,user=self.username,password=self.password,port=self.port,dbname=self.database)
        cursor=conn.cursor()
        cursor.execute(query)
        result=cursor.fetchall()
        df=pd.DataFrame(result)
        col_name=[name[0] for name in cursor.description]
        df.columns=col_name
        return df
    
    def query_iteration(self,query,iteration):
        conn=psycopg2.connect(host=self.hostname,user=self.username,password=self.password,port=self.port,dbname=self.database)
        cursor=conn.cursor()
        cursor.execute(query.format(iteration))
        result=cursor.fetchall()
        df=pd.DataFrame(result)
        col_name=[name[0] for name in cursor.description]
        df.columns=col_name
        return df
    
    def query_tovar(self,query):
        conn=psycopg2.connect(host=self.hostname,user=self.username,password=self.password,port=self.port,dbname=self.database)
        cursor=conn.cursor()
        cursor.execute(query)
        result=cursor.fetchall()
        return result