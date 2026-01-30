from django.apps import AppConfig


class PropertiesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'properties'
    
    def ready(self):
        # Import signals if they exist
        try:
            import properties.signals
        except ImportError:
            pass
