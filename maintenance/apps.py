from django.apps import AppConfig


class MaintenanceConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'maintenance'
    
    def ready(self):
        # Import signals if they exist
        try:
            import maintenance.signals
        except ImportError:
            pass
