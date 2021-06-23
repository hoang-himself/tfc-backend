from django.apps import AppConfig


class DatabaseAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'master_db'
    verbose_name = 'User Database'
