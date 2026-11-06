"""Ícones (Font Awesome) de apps e models no menu e nos cards do admin.

- App: atributo ``icon`` do ``AppConfig``; sem ele, ``settings.DSGOVBR_DEFAULT_APP_ICON``
  (padrão ``DEFAULT_APP_ICON``).
- Model: atributo ``icon`` do ``ModelAdmin`` (o ``class Meta`` do model não aceita
  atributos desconhecidos); sem ele, ``settings.DSGOVBR_DEFAULT_MODEL_ICON``
  (padrão ``DEFAULT_MODEL_ICON``).
- Item registrado no ``menus.py`` sem ícone: ``settings.DSGOVBR_DEFAULT_MENU_ICON``
  (padrão ``DEFAULT_MENU_ICON``).
"""

from typing import Any

from django.apps import apps
from django.conf import settings

DEFAULT_APP_ICON = "fas fa-folder"
DEFAULT_MODEL_ICON = "fas fa-table"
DEFAULT_MENU_ICON = "fas fa-angle-right"


def default_app_icon() -> str:
    return getattr(settings, "DSGOVBR_DEFAULT_APP_ICON", "") or DEFAULT_APP_ICON


def default_model_icon() -> str:
    return getattr(settings, "DSGOVBR_DEFAULT_MODEL_ICON", "") or DEFAULT_MODEL_ICON


def default_menu_icon() -> str:
    return getattr(settings, "DSGOVBR_DEFAULT_MENU_ICON", "") or DEFAULT_MENU_ICON


def app_icon(app_label: str | None) -> str:
    """Ícone do app pelo ``AppConfig.icon`` ou o padrão."""
    if not app_label:
        return default_app_icon()
    try:
        config = apps.get_app_config(app_label)
    except LookupError:
        return default_app_icon()
    return getattr(config, "icon", "") or default_app_icon()


def model_icon(model: Any, site: Any = None) -> str:
    """Ícone do model pelo ``ModelAdmin.icon`` registrado no ``site`` ou o padrão."""
    if model is None:
        return default_model_icon()
    if site is None:
        from django.contrib import admin

        site = admin.site
    model_admin = getattr(site, "_registry", {}).get(model)
    return getattr(model_admin, "icon", "") or default_model_icon()
