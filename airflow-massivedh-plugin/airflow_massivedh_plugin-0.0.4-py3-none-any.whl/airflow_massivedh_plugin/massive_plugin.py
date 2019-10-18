# This is the class you derive to create a plugin
from airflow.plugins_manager import AirflowPlugin

# Importing base classes that we need to derive
from airflow.hooks.base_hook import BaseHook
from airflow.models import BaseOperator
from airflow.models.baseoperator import BaseOperatorLink
from airflow.sensors.base_sensor_operator import BaseSensorOperator
from airflow.executors.base_executor import BaseExecutor

# Will show up under airflow.hooks.test_plugin.PluginHook
class PluginHook(BaseHook):
    pass
    
# Will show up under airflow.operators.airflow_massivedh_plugin.Auth2LogoutOperator
class Auth2LogoutOperator(SimpleHttpOperator):
    def __init__(self,task_id,dag=None):
        super(MassiveLogoutOperator, self).__init__(
            task_id=task_id,
            dag=dag,
            method='DELETE',
            endpoint='auth/v2/authentication',
            http_conn_id = 'massive_auth2',
            xcom_push=True,
            log_response=True
        )
        
    def execute(self, context):
        print("Auth2LogoutOperator") 
        response = json.loads(self.xcom_pull(context, task_ids='login_op',key='return_value'))
        token = response["token"]
        self.headers = {"Authorization": "Bearer " + token }
        print( "header: " + str(self.headers) )
        
        super(MassiveLogoutOperator, self).execute(context)
        print("MassiveLogoutOperator -- end")
        
# Will show up under airflow.sensors.test_plugin.PluginSensorOperator
class PluginSensorOperator(BaseSensorOperator):
    pass

# Will show up under airflow.executors.test_plugin.PluginExecutor
class PluginExecutor(BaseExecutor):
    pass

# Will show up under airflow.macros.test_plugin.plugin_macro
# and in templates through {{ macros.test_plugin.plugin_macro }}
def plugin_macro():
    pass

# A global operator extra link that redirect you to
# task logs stored in S3
class S3LogLink(BaseOperatorLink):
    name = 'S3'

    def get_link(self, operator, dttm):
        return 'https://s3.amazonaws.com/airflow-logs/{dag_id}/{task_id}/{execution_date}'.format(
            dag_id=operator.dag_id,
            task_id=operator.task_id,
            execution_date=dttm,
        )


# Defining the plugin class
class MassiveAirflowPlugin(AirflowPlugin):
    name = "massive_plugin"
    operators = [Auth2LogoutOperator]
    sensors = [PluginSensorOperator]
    hooks = [PluginHook]
    executors = [PluginExecutor]
    macros = [plugin_macro]
    admin_views = []
    flask_blueprints = []
    menu_links = []
    appbuilder_views = []
    appbuilder_menu_items = []
    global_operator_extra_links = [S3LogLink(),]