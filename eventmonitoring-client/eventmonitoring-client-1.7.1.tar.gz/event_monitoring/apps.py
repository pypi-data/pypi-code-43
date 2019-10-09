try:
    from django.apps import AppConfig
    
    class ApiConfig(AppConfig):
        name = 'event_monitoring'
except ImportError:
    pass
