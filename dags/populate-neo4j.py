
from airflow import DAG

from datetime import timedelta, datetime
from airflow.utils.dates import days_ago

from airflow.operators.bash import BashOperator


args = {
    'owner': 'Joao Brito',
    'start_date': days_ago(1) 
}

dag = DAG(
    dag_id='populate-neo4j-dag',
    default_args=args,
    schedule_interval='@daily' 
)

create_command = " python3 ./src/extract_data.py"

t1 = BashOperator(
    task_id= 'populate_database',
    bash_command=create_command,
    dag=dag
)
