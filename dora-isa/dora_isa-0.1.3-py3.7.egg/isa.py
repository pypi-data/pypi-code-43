import re, os,json, datetime
import pymysql, sqlparse, hashlib
import requests, boto3
from time import sleep
from delta.tables import DeltaTable
from IPython.core import magic_arguments
from IPython.core.magic import Magics

AWS_REGION    = os.environ.get('AWS_REGION','us-east-1')
STATE_MACHINE = os.environ.get('AWS_STATE_MACHINE','arn:aws:states:us-east-1:229343956935:stateMachine:benny-import-data')
BENNY_ARN     = os.environ.get('BENNY_ARN','arn:aws:lambda:us-east-1:229343956935:function:benny')
CACHE_DB      = os.environ.get('CACHE_DB','cache')
DELTA_DB      = os.environ.get('DELTA_DB','delta')
DORA_BUCKET   = os.environ.get('S3_BUCKET','autonomous-sandbox')
ADHOC_DB      = os.environ.get('ADHOC_DB','adhoc')
DORA_USER     = os.environ.get('DORA_USER')

class ISAContext:
    """
    Contextualiza as consultas a serem executadas
    """
    r_date=r"""'([0-9]{4}-[0-9]{2}-[0-9]{2})'"""
    r_version=r"""'[0-9]{1,}'"""
    r_table = r"""(?:[\s]+)([\d\w\$_]+\.[\d\w\$_]+\.[\d\w\$_]+)(?:(?:[\s])+|\Z|;|\))"""
    r_drop = f"""DROP[\s]?TABLE[\s]?{r_table}"""
    r_delta = f"""{r_table}(asof+)(?:(?:[\s])+|\Z|\))({r_date}|{r_version})"""
    table_status ="""SELECT * FROM isa.table_status WHERE full_name_table = %s """
    
    def __init__(self,spark,debug=False):
        """
        Parameters
        ----------
        spark : object
            recebe o contexto spark
        schema : str
            default: 'cache'
            Identificador do schema de chache no metastore do dora
        debug : boolean
            quando true ativa o modo debug
        """
        self.spark = spark
        self.debug = debug
        self.steps = boto3.client('stepfunctions',AWS_REGION)
        self.spark.sql(f"""CREATE DATABASE IF NOT EXISTS {ADHOC_DB} LOCATION 's3a://{DORA_BUCKET}/{ADHOC_DB}/'""")
        self.spark.sql(f"""CREATE DATABASE IF NOT EXISTS {CACHE_DB} LOCATION 's3a://{DORA_BUCKET}/{CACHE_DB}/'""")
        self.spark.sql(f"""CREATE DATABASE IF NOT EXISTS {DELTA_DB} LOCATION 's3a://{DORA_BUCKET}/{DELTA_DB}/'""")
        
    def printd(self,*messages):
        """
        Utilitário usado para exibir as mensagem quando o modo debug está ativado
        ----------
        messages : list
            Lista de todas as mensagems a serem printadas 
        """
        if self.debug:
            for message in messages:
                print(message)
    
    def get_table_status(self,table_list):
        """
        Consulta os metadados das tabelas solicitadas no Dora Metastore
        ----------
        table_list : list
            Lista de todas as tabelas solicitadas na query 
        Returns
        -------
        Dict
            Retorna um dicionário com os metadados de todas as tabelas solicitadas
        """
        connection = pymysql.connect( host=os.environ['HIVE_BASE']
                                    , user=os.environ['HIVE_USER']
                                    , password=os.environ['HIVE_PASS']
                                    , db='isa',cursorclass=pymysql.cursors.DictCursor)
        table_meta=dict()
        try:
            with connection.cursor() as cursor:
                for table_id in table_list:
                    cursor.execute(self.table_status, (table_id.upper().replace('.','_'),))
                    table_meta[table_id] = cursor.fetchone()
                    if table_meta[table_id] is not None:
                        if table_meta[table_id].get('nextUpdate') <= datetime.datetime.now():
                            print(f"{table_id} is outdated: {table_meta[table_id].get('lastUpdate')} ({table_meta[table_id].get('cacheDays')} days)")
                            table_meta[table_id] = None
                        else:
                            print(f"{table_id} is updated: {table_meta[table_id].get('lastUpdate')} ({table_meta[table_id].get('cacheDays')} days)")
                    else:
                        print(f"{table_id} is now loading")
            return table_meta
        finally:
            connection.close()
    
    def load_tables(self, table_list):
        """
        Agenda a execução de todas as tableas que precisam ser atualizadas
        ----------
        table_list : list
            Lista de todas as tabelas desatualizadas 
        Returns
        -------
        List
            Retorna a lista das execuções agendadas via Step-Function
        """
        responses=list()
        for table in table_list:
            conn,schema,table=table.split('.')
            input_data={"username": os.environ['DORA_USER'],"connection_name": conn,"schema": schema,"table": table}
            response=self.steps.start_execution(stateMachineArn=STATE_MACHINE,input=json.dumps(input_data))
            responses.append(response)
        return responses
    
    def wait_execution(self, executions):
        """
        Verifica o andamento das Step-Functions em execução
        ----------
        executions : list
            Lista de todas as execuções em andamento 
        Returns
        -------
        List
            Retorna a lista das execuções concluídas
        """
        responses=list()
        while len(executions) > 0:
            sleep(2)
            for execution in executions:
                execution_status=self.steps.describe_execution(executionArn=execution['executionArn'])
                if execution_status.get('status') != 'RUNNING':
                    responses.append(execution_status)
                    input_data = json.loads(execution_status['input'])
                    self.printd('execution_status',execution_status)
                    cache_table = f"{CACHE_DB}.{input_data['connection_name']}_{input_data['schema']}_{input_data['table']}"
                    self.spark.sql(f"REFRESH TABLE {cache_table}")
                    executions.remove(execution)
        return responses
    
    def creat_version_of(self, table, version, alias):
        c,s,t = table.split('.')
        delta_path = f"s3a://{DORA_BUCKET}/{DELTA_DB}/{c}_{s}_{t}"
        table_history = f"h_{c}_{s}_{t}"
        try:
            self.spark.catalog.isCached(table_history)
        except:
            DeltaTable.forPath(self.spark, delta_path).history().createOrReplaceTempView(table_history).cache()
        try:
            v = re.findall(self.r_version,version,re.IGNORECASE)[0].replace("'","")
            r = self.spark.sql(f"""SELECT * FROM (
                              SELECT timestamp `dt`,version `v` FROM {table_history} WHERE version = {v} UNION ALL
                              SELECT timestamp `dt`,version `v` FROM {table_history} WHERE version = 0) ORDER BY 2 DESC""").take(1)
        except:
            dt = re.findall(self.r_date,version,re.IGNORECASE)[0]
            r = self.spark.sql(f"""SELECT * FROM(SELECT * FROM (SELECT max(timestamp)`dt`,max(version)`v` FROM {table_history} WHERE date_trunc('DD',timestamp)<='{dt}' 
                              GROUP BY date_trunc('DD',timestamp) ORDER BY 1 DESC LIMIT 1) UNION ALL SELECT timestamp `dt`,version `v` FROM {table_history} WHERE version = 0) ORDER BY 2 DESC""").take(1)
        v = r[0].v
        table_name = f"v{v}_{c}_{s}_{t}"
        print(f"{alias} -> {r[0].dt.strftime('%Y-%m-%d %H:%M:%S')}")
        try:
            self.spark.catalog.isCached(table_name)
        except:
            self.spark.read.format("delta").option("versionAsOf", v).load(delta_path).createOrReplaceTempView(table_name)
        return table_name
    
    def sql_parser(self, sql):
        p = sqlparse.parse(sql)
        for s in sqlparse.parse(sql):
            if s.get_type() != 'SELECT':
                raise ValueError(f"Only 'SELECT' statements are allowed")
            q = list()
            for k,v in enumerate(s.tokens):
                if v.is_whitespace:
                    continue
                if v.is_keyword:
                    q.append(v.normalized.upper())
                else:
                    q.append(v.normalized)
            return q
        
    def sql(self, query, args):
        """
        Executa query usando SparkSQL
        ----------
        query : string
            Recebe a query bruta.
        Returns
        -------
        Dataframe
            retorna o dataframe da query.
        """
        self.debug = args.verbose
        self.printd(args)
        
        if args.connection is not None:
            parser = self.sql_parser(query)
            table_name = hashlib.sha1(''.join(parser).encode('utf8')).hexdigest()
            try:
                return self.spark.table(f"{ADHOC_DB}.{table_name}")
            except Exception as e:
                client = boto3.client('lambda',AWS_REGION)
                payload = {"adhoc": True,"username": DORA_USER,"connection_name": args.connection,"schema": ADHOC_DB,"table": table_name,"query": query.replace("\n"," ")}
                self.printd(json.dumps(payload))
                response = client.invoke(
                    FunctionName=BENNY_ARN,
                    InvocationType='RequestResponse',
                    Payload=bytes(json.dumps(payload).encode('utf8')))
                self.printd(response)
                self.printd(response.get('Payload').read().decode('utf8'))
                return self.spark.table(f"{ADHOC_DB}.{table_name}")
        
        if len(re.findall(self.r_drop,query,re.MULTILINE | re.IGNORECASE)) > 0:
            raise ValueError(f"Is not possible to DROP a DORA's external table")

        using_delta=False
        for n, match in enumerate(re.finditer(self.r_delta, query, re.MULTILINE | re.IGNORECASE), start=1):
            using_delta=True
            table_name= self.creat_version_of(match.group(1),match.group(3),match.group(0))
            query=query.replace(match.group(0),f" {table_name}")
        if using_delta:
            self.printd("delta_query",query)
        # return True
        table_list = set([v.group(1) for k,v in enumerate(re.finditer(self.r_table, query, re.MULTILINE | re.IGNORECASE), start=1)])
        if len(table_list)>0:
            self.printd('table_list',table_list)
        table_meta = self.get_table_status(table_list)
        if len(table_meta)>0:
            self.printd('table_meta',table_meta)
        # Lista de execuções submetidas por este sandbox
        executions = self.load_tables([t for t in table_meta if table_meta[t] is None])
        # Lista de execuções em andamento por outros sandboxes
        for execution in [{'executionArn':table_meta[t]['execution']} for t in table_meta if table_meta[t] is not None and table_meta[t].get('status') == 'loading']:
            executions.append(execution)
        if len(executions)>0:
            self.printd('executions',executions)
        for execution in self.wait_execution(executions):
            if execution['status']=='FAILED':
                input_data = json.loads(execution['input'])
                raise ValueError(f"FAIL to load '{input_data['connection_name']}.{input_data['schema']}.{input_data['table']}'")
        for t in table_meta:
            if table_meta[t] is None:
                conn,schema,table=t.split('.')
                table_id = f"{conn}_{schema}_{table}"
                query=query.replace(t,f"{CACHE_DB}.{table_id}")
            else:
                table_id = f"{CACHE_DB}.{table_meta[t]['table_id']}"
                query=query.replace(t,table_id)
        self.printd(query)
        return self.spark.sql(query)

class ISAMagic(Magics):
    from IPython.core.magic import register_cell_magic
    ipython  = get_ipython()
    
    def __init__(self,ISAContext):
        self.isa = ISAContext
        self.ipython.register_magic_function(self.sql, 'cell')

    @magic_arguments.magic_arguments()
    @magic_arguments.argument('--connection', '-c', default=None, help='Connection Name')
    @magic_arguments.argument('--limit', '-l', type=int, default=100, help='Result set limit')
    @magic_arguments.argument('--verbose', '-v',action='store_true',help='Print Debug messages')
    @magic_arguments.argument('--out', '-o',help='The variable to return the results in')
    def sql(self, line, query):
        args = magic_arguments.parse_argstring(self.sql, line)
        if args.out is None:
             return self.isa.sql(query,args).limit(args.limit).toPandas()
        else:
            df = self.isa.sql(query,args)
            self.ipython.user_ns[args.out] = df
            return df
