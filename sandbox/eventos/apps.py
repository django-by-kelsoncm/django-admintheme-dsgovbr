from django.apps import AppConfig


class EventosConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "eventos"
    verbose_name = "Gestão de Eventos"
    icon = "fas fa-calendar-alt"
