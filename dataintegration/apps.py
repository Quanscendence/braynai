from django.apps import AppConfig
import analytics


class DataintegrationConfig(AppConfig):
    name = 'dataintegration'
    def ready(self):
        analytics.write_key = 'Oxs5kf1oUqpuHshCBNBaplt6qd7thgzF'
