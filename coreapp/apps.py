from django.apps import AppConfig
from actstream import registry
from django.contrib.auth.models import User
from coreapp.models import Project

class CoreappConfig(AppConfig):
    name = 'coreapp'
    def ready(self):
        registry.register(User,self.get_model('ProjectType'),self.get_model('Project'),self.get_model('ProjectUser'),self.get_model('ProjectColumn'),self.get_model('ProjectDashboard'))
