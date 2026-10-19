from django.apps import AppConfig


class TasksConfig(AppConfig):
    """
    Application configuration for 'tasks'.
    Django uses this class to configure the app when it starts.
    """
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tasks'
    verbose_name = 'Task Management'
