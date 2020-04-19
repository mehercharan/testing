from datetime import timedelta

from airflow import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.dummy_operator import DummyOperator
from airflow.utils.dates import days_ago
from airflow.operators.slack_operator import SlackAPIPostOperator
from airflow.hooks.base_hook import BaseHook
from airflow.contrib.operators.slack_webhook_operator import SlackWebhookOperator

SLACK_CONN_ID = 'slack'
def task_fail_slack_alert(context):
    slack_webhook_token = BaseHook.get_connection(SLACK_CONN_ID).password
    slack_msg = """
            :red_circle: Task Failed. 
            *Task*: {task}  
            *Dag*: {dag} 
            *Execution Time*: {exec_date}  
            *Log Url*: {log_url} 
            """.format(
            task=context.get('task_instance').task_id,
            dag=context.get('task_instance').dag_id,
            ti=context.get('task_instance'),
            exec_date=context.get('execution_date'),
            log_url=context.get('task_instance').log_url,
        )
    failed_alert = SlackWebhookOperator(
        task_id='slack_test',
        http_conn_id='slack',
        webhook_token=slack_webhook_token,
        message=slack_msg,
        username='airflow')
    return failed_alert.execute(context=context)



args = {
    'owner': 'airflow',
    'start_date': days_ago(2),
    'on_failure_callback': task_fail_slack_alert
}
#slack_token = BaseHook.get_connection(SLACK_CONN_ID).password

dag = DAG(
    dag_id='meat_dag',
    default_args=args,
    schedule_interval='0 0 * * *',
    dagrun_timeout=timedelta(minutes=60)
)

task_with_failed_slack_alerts = BashOperator(
    task_id='fail_task',
    bash_command='exit 1',
    on_failure_callback=task_fail_slack_alert,
    provide_context=True,
    dag=dag)

#dummy_task = DummyOperator(task_id='dummy_task',dag=dag,retries=3)







# [END howto_operator_bash_template]
#dummy_task
