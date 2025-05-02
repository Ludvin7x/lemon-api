# LittleLemonAPI/apps.py
from django.apps import AppConfig

class LittlelemonapiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'LittleLemonAPI'

def ready(self):
        from .initial_data import load_initial_data
        load_initial_data()