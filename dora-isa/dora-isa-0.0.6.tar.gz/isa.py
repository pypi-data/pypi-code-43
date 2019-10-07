import re, os,json, datetime
import pymysql, sqlparse
import requests, boto3
from time import sleep
from delta.tables import DeltaTable

AWS_REGION    = os.environ.get('AWS_REGION','us-east-1')
STATE_MACHINE = os.environ.get('AWS_STATE_MACHINE','arn:aws:states:us-east-1:229343956935:stateMachine:benny-import-data')
CACHE_DB      = os.environ.get('CACHE_DB','cache')
DELTA_DB      = os.environ.get('DELTA_DB','delta')
DORA_BUCKET   = os.environ.get('S3_BUCKET','autonomous-sandbox')

class ISAContext:
    """
    Contextualiza as consultas a serem executadas
    """
    d_regex=r"""'([0-9]{4}-[0-9]{2}-[0-9]{2})'"""
    v_regex=r"""'[0-9]{1,}'"""
    table_regex = r"""(?:[\s]+)([\d\w\$_]+\.[\d\w\$_]+\.[\d\w\$_]+)(?:(?:[\s])+|\Z|;|\))"""
    drop_regex = f"""DROP[\s]?TABLE[\s]?{table_regex}"""
    delta_regex = f"""{table_regex}(asof+)(?:(?:[\s])+|\Z|\))({d_regex}|{v_regex})"""
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
        self.cache_schema = CACHE_DB
        self.steps = boto3.client('stepfunctions',AWS_REGION)
                    
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
            spark.catalog.isCached(table_history)
        except expression as identifier:
            DeltaTable.forPath(self.spark, delta_path).history().createOrReplaceTempView(table_history).cache()
        try:
            v = re.findall(self.v_regex,version,re.IGNORECASE)[0].replace("'","")
            r = spark.sql(f"""SELECT * FROM (
                              SELECT timestamp `dt`,version `v` FROM {table_history} WHERE version = {v} UNION ALL
                              SELECT timestamp `dt`,version `v` FROM {table_history} WHERE version = 0) ORDER BY 2 DESC""").take(1)
        except:
            dt = re.findall(self.d_regex,version,re.IGNORECASE)[0]
            r = spark.sql(f"""SELECT * FROM ( SELECT * FROM (SELECT max(timestamp)`dt`,max(version)`v` 
                                                FROM {table_history} WHERE date_trunc('DD',timestamp)<='{dt}' 
                                           GROUP BY date_trunc('DD',timestamp) ORDER BY 1 DESC LIMIT 1) UNION ALL
                              SELECT timestamp `dt`,version `v` FROM {table_history} WHERE version = 0) ORDER BY 2 DESC""").take(1)
        v = r[0].v
        table_name = f"v{v}_{c}_{s}_{t}"
        print(f"{alias} -> {r[0].dt.strftime('%Y-%m-%d %H:%M:%S')}")
        try:
            spark.catalog.isCached(table_name)
        except:
            self.spark.read.format("delta").option("versionAsOf", v).load(delta_path).createOrReplaceTempView(table_name)
        return table_name

    def sql(self, query):
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
        
        if len(re.findall(self.drop_regex,query,re.MULTILINE | re.IGNORECASE)) > 0:
            raise ValueError(f"Is not possible to DROP a DORA's external table")

        using_delta=False
        for n, match in enumerate(re.finditer(self.delta_regex, query, re.MULTILINE | re.IGNORECASE), start=1):
            using_delta=True
            table_name= self.creat_version_of(match.group(1),match.group(3),match.group(0))
            query=query.replace(match.group(0),f" {table_name}")
        if using_delta:
            self.printd("delta_query",query)
        # return True
        table_list = set([v.group(1) for k,v in enumerate(re.finditer(self.table_regex, query, re.MULTILINE | re.IGNORECASE), start=1)])
        self.printd('table_list',table_list)
        table_meta = self.get_table_status(table_list)
        self.printd('table_meta',table_meta)
        # Lista de execuções submetidas por este sandbox
        executions = self.load_tables([t for t in table_meta if table_meta[t] is None])
        # Lista de execuções em andamento por outros sandboxes
        for execution in [{'executionArn':table_meta[t]['execution']} for t in table_meta if table_meta[t] is not None and table_meta[t].get('status') == 'loading']:
            executions.append(execution)
        self.printd('executions',executions)
        for execution in self.wait_execution(executions):
            if execution['status']=='FAILED':
                input_data = json.loads(execution['input'])
                raise ValueError(f"FAIL to load '{input_data['connection_name']}.{input_data['schema']}.{input_data['table']}'")
        for t in table_meta:
            if table_meta[t] is None:
                conn,schema,table=t.split('.')
                table_id = f"{conn}_{schema}_{table}"
                query=query.replace(t,f"{self.cache_schema}.{table_id}")
            else:
                table_id = f"{self.cache_schema}.{table_meta[t]['table_id']}"
                query=query.replace(t,table_id)
        self.printd("= QUERY =",query)
        return self.spark.sql(query)
    
class ISAMagic:
    from IPython.core.magic import register_cell_magic
    from IPython.core import magic_arguments as magic_arg
    ipython  = get_ipython()
    
    def __init__(self,ISAContext,limit=50):
        self.isa = ISAContext
        self.limit = limit
        self.ipython.register_magic_function(self.sql, 'cell')

    @magic_arg.magic_arguments()
    @magic_arg.argument('connection', nargs='?', default=None)
    def sql(self, line, cell):
        # print("limited by {} results".format(self.limit))
        return self.isa.sql(cell).limit(self.limit).toPandas()
        return self.isa.sql(cell)

dora=ISAContext(spark,debug=False)
ISAMagic(dora)