from django.apps import AppConfig
from actstream import registry
from django.contrib.auth.models import User


class LoginConfig(AppConfig):
    name = 'login'
    def ready(self):
        registry.register(User,self.get_model('Customer'))
