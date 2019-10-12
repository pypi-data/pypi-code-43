from os import getenv

from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from datetime import datetime, timedelta

from finance_scraping.main import extract, transform, load

default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': datetime.strptime(
        getenv('FINANCE_SCRAPING_DAG_START_DATE'),
        '%Y-%m-%dT%H:%M'),
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=20)
}

dag = DAG(
    'finance_scraping_etl',
    default_args=default_args,
    schedule_interval='0 22 * * 1-5'
)

extract_task = PythonOperator(
    task_id='extract',
    python_callable=extract,
    dag=dag
)

transform_task = PythonOperator(
    task_id='transform',
    python_callable=transform,
    dag=dag
)

load_task = PythonOperator(
    task_id='load',
    python_callable=load,
    dag=dag
)

extract_task >> transform_task >> load_task
