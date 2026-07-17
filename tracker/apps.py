from django.apps import AppConfig


class TrackerConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tracker'

    def ready(self):
        # Import signal handlers so they get registered when the app is ready
        import tracker.signals  # noqa: F401
