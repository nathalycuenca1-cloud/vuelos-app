from django.apps import AppConfig
from django.db.models.signals import post_migrate


def crear_grupos_post_migrate(sender, **kwargs):
    from django.contrib.auth.management import create_permissions
    from vuelos.grupos import crear_grupos
    create_permissions(sender, verbosity=0)
    crear_grupos()


class VuelosConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'vuelos'
    verbose_name = 'Reserva de vuelos'

    def ready(self):
        post_migrate.connect(crear_grupos_post_migrate, sender=self)
