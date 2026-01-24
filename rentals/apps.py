from django.apps import AppConfig


class RentalsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'rentals'
    verbose_name = 'Rental Management System'
    
    def ready(self):
        import rentals.signals  # noqa
