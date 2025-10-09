from django.apps import AppConfig


class PlatformConfig(AppConfig):
    """AppConfig for the platform package.

    We set a stable app label ('platform') so Django references (like
    AUTH_USER_MODEL) are predictable and not tied to the module path.
    """

    name = 'src.platform'
    label = 'platform'

    def ready(self):
        """Import models when app is ready."""
        pass
