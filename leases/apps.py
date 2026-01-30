from django.apps import AppConfig


class LeasesConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'leases'
    
    def ready(self):
        # Import signals if they exist
        try:
            import leases.signals
        except ImportError:
            pass
