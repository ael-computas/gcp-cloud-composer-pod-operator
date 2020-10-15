# -*- coding: utf-8 -*-
class Tolerations():
    def __init__(self):
        pass

    default = [
        {
            'key': "workshop",
            'operator': 'Equal',
            'value': 'custom',
            'effect': "NoSchedule"
        }
    ]


class Affinity():
    def __init__(self):
        pass

    memory_heavy = {
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
