# -*- coding: utf-8 -*-
from airflow import models
from airflow.utils.dates import days_ago
from airflow.operators.bash_operator import BashOperator
from airflow.operators.dummy_operator import DummyOperator
from airflow.contrib.operators import kubernetes_pod_operator

tolerations = [
    {
        'key': "workshop",
        'operator': 'Equal',
        'value': 'custom',
        'effect': "NoSchedule"
    }
]

aff = {
    'nodeAffinity': {
        'requiredDuringSchedulingIgnoredDuringExecution': {
            'nodeSelectorTerms': [{
                'matchExpressions': [{
                    'key': 'cloud.google.com/gke-nodepool',
                    'operator': 'In',
                    'values': [
                        'memory-heavy'
                    ]
                }]
            }]
        }
    }
}

with models.DAG(
    "combined_example_resource_shortage_fails",
    schedule_interval=None,  # Override to match your needs
    start_date=days_ago(1),
    concurrency=10,
    tags=['example3'],
) as dag:
    start_task = DummyOperator(task_id="start")
    start_processing = DummyOperator(task_id="start_processing")
    end_task = DummyOperator(task_id="end")
    source_1_task = BashOperator(
        bash_command="echo \"Pretending to be source 1\"; sleep 20",
        task_id="source_1",
    )
    source_2_task = BashOperator(
        bash_command="echo \"Pretending to be source 2\"; sleep 20",
        task_id="source_2",
    )
    processing_tasks = []
    for i in range(1, 11):
        processing_tasks.append(kubernetes_pod_operator.KubernetesPodOperator(
            task_id='3Gi-task_{}'.format(i),
            name='3Gi-task-{}'.format(i),
            cmds=["sh", "-c", 'echo \'Sleeping..\'; sleep 120; echo \'Done!\''],
            namespace='default',
            resources={'request_memory': '3Gi',
                       'request_cpu': '200m',
                       'limit_memory': '3Gi',
                       'limit_cpu': 1},
            image='gcr.io/gcp-runtimes/ubuntu_18_0_4',
            tolerations=tolerations,
            affinity=aff,
            startup_timeout_seconds=60,
        ))

    start_task >> source_1_task >> start_processing
    start_task >> source_2_task >> start_processing
    for task in processing_tasks:
        start_processing >> task >> end_task
