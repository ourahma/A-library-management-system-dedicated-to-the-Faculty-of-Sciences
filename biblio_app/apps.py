from django.apps import AppConfig


class BiblioAppConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'biblio_app'
    def ready(self):
        import biblio_app.signals 