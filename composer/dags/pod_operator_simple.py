# -*- coding: utf-8 -*-
import datetime

from airflow import models
from airflow.contrib.kubernetes import secret
from airflow.contrib.operators import kubernetes_pod_operator
from utils.kubernetes import Tolerations, Affinity

YESTERDAY = datetime.datetime.now() - datetime.timedelta(days=1)

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
        dag_id='composer_kubernetes_pod_simple',
        schedule_interval=None,
        start_date=YESTERDAY) as dag:
    kubernetes_min_pod = kubernetes_pod_operator.KubernetesPodOperator(
        task_id='pod-workshop-simple',
        name='pod-workshop-simple',
        cmds=['echo', '"Hello world"'],
        namespace='default',
        resources={'request_memory': '128Mi',
                   'request_cpu': '500m',
                   'limit_memory': '500Mi',
                   'limit_cpu': 1},
        image='gcr.io/gcp-runtimes/ubuntu_18_0_4',
        tolerations=Tolerations.default,
        affinity=Affinity.memory_heavy
    )
