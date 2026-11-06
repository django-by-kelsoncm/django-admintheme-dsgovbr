from django.conf import settings
from django.http import HttpRequest
from django.contrib import admin
from django.urls import get_script_prefix, reverse
from django.utils import timezone


def _get_element_as_list(dictionary: dict, name: str) -> list:
    setting = dictionary.get(name, [])
    return setting if isinstance(setting, list) else []


def _logout_url() -> str:
    """URL de saída: a rota ``logout`` do projeto ou, na falta dela, a do admin."""
    from django.urls import NoReverseMatch

    for name in ("logout", "admin:logout"):
        try:
            return reverse(name)
        except NoReverseMatch:
            continue
    return ""


def layout_settings(request: HttpRequest) -> dict:
    project_company = getattr(settings, "PROJECT_COMPANY", "Minha empresa")
    project_title = getattr(settings, "PROJECT_TITLE", "Nome do projeto")
    project_subtitle = getattr(settings, "PROJECT_SUBTITLE", "Slogan do projeto")
    site_admin_atual = admin.site

    dsgovbr_dict = {
        "header": {
            **{
                "type": "default",
                "width_style": "lg",  # Bootstrap: sm|md|lg|xl|xxl|fluid
                "logo": {
                    "show": True,
                    "type": "compact",
                    "default_url": "https://www.gov.br/ds/assets/img/govbr-logo.png",
                    "compact_url": "https://www.gov.br/ds/assets/img/govbr-logo.png",
                    "link": "https://www.gov.br/pt-br",
                },
                "assinatura": {
                    "show": False,
                    "label": project_company,
                },
                "titulo": {
                    "label": project_title,
                },
                "subtitulo": {
                    "show": str(project_subtitle or "") != "",
                    "label": project_subtitle,
                },
                "links": {
                    "show": False,
                    # True: links em linha a partir de 1200px (dropdown abaixo disso)
                    "em_linha": False,
                    "items": [],
                },
                "funcionalidades": {
                    "show": False,
                    # True: ícones em linha a partir de 1200px (dropdown abaixo disso)
                    "em_linha": False,
                    "items": [],
                },
                "login": {
                    "show": True,
                    "type": "default",
                    "default_avatar_url": "",
                    "saudacao": "Olá, ",
                    "name_to_show": "first",
                    "dropdown": {
                        "show": True,
                        "show_large_avatar": True,
                        "show_full_name": True,
                        "show_role": True,
                        "items": [
                            {
                                "label": "Sair",
                                "url": _logout_url(),
                                # LogoutView (Django 5+) só aceita POST
                                "method": "post",
                                "icon": "fas fa-sign-out-alt",
                            },
                        ],
                    },
                },
                "menu": {
                    "show": True,
                    "localizacao": "flutuante",  # flutuante (offcanvas)|fixo (aberto a partir de 1200px)
                    "padding": {},
                    "header": {},
                    # rodapé do menu: logos [{src, alt}], links [{label, url, icon, target}],
                    # redes_sociais [{label, icon, url}] e licenca (texto)
                    "footer": {
                        "logos": [],
                        "links": [],
                        "redes_sociais": [],
                        "licenca": "",
                    },
                    "items": "",
                },
                "search": {
                    "ativo": True,
                },
                "responsive_dropdown": {"show": True},
            },
            **getattr(settings, "DSGOVBR_HEADER", {}),
        },
        "footer": {
            **{
                "show": True,
                # logo (versão negativa) e assinatura: {src, alt}
                "logo": None,
                # colunas: [{titulo, links: [{label, url, target}]}]
                "colunas": [],
                # redes_sociais: [{label, icon, url}]
                "redes_sociais": [],
                "assinatura": None,
                # texto antes do copyright na última linha
                "texto": "",
            },
            **getattr(settings, "DSGOVBR_FOOTER", {}),
        },
        "login": {
            **{
                "show": True,
                "alternative_methods": [],
            },
            **getattr(settings, "DSGOVBR_LOGIN", {}),
        },
    }

    # Normalize and resolve search options
    from django.urls import NoReverseMatch

    header_search = dsgovbr_dict["header"].get("search", {})

    if isinstance(header_search, bool):
        header_search = {"ativo": header_search}
    elif not isinstance(header_search, dict):
        header_search = {}

    search_ativo = header_search.get("ativo", header_search.get("show", True))
    search_view_name = header_search.get("view_name", "site_search")

    autocomplete_config = header_search.get("autocomplete", {})
    if isinstance(autocomplete_config, bool):
        autocomplete_config = {"ativo": autocomplete_config}
    elif not isinstance(autocomplete_config, dict):
        autocomplete_config = {}

    autocomplete_ativo = autocomplete_config.get(
        "ativo", autocomplete_config.get("show", False)
    )
    autocomplete_view_name = autocomplete_config.get(
        "view_name", "site_index_autocomplete"
    )

    # Resolve search view URL
    search_show = False
    search_url = ""
    if search_ativo:
        try:
            search_url = reverse(search_view_name)
            search_show = True
        except NoReverseMatch:
            search_show = False

    # Resolve autocomplete view URL
    autocomplete_show = False
    autocomplete_url = ""
    if search_show and autocomplete_ativo:
        try:
            autocomplete_url = reverse(autocomplete_view_name)
            autocomplete_show = True
        except NoReverseMatch:
            autocomplete_show = False

    dsgovbr_dict["header"]["search"] = {
        "ativo": search_ativo,
        "view_name": search_view_name,
        "show": search_show,
        "url": search_url,
        "autocomplete": {
            "ativo": autocomplete_ativo,
            "view_name": autocomplete_view_name,
            "show": autocomplete_show,
            "url": autocomplete_url,
        },
    }

    return {
        "project_company": project_company,
        "project_title": project_title,
        "project_subtitle": project_subtitle,
        "project_version": getattr(settings, "PROJECT_VERSION", "v1.0.0"),
        # início do site: PROJECT_HOME_URL ou o prefixo do script (FORCE_SCRIPT_NAME/subcaminho)
        "project_home_url": getattr(settings, "PROJECT_HOME_URL", "")
        or get_script_prefix(),
        # prefixo da página da versão (ex.: ".../releases/tag/"); vazio: a versão aparece sem link
        "project_releases_url": getattr(settings, "PROJECT_RELEASES_URL", ""),
        "project_last_startup": getattr(
            settings, "PROJECT_LAST_STARTUP", str(timezone.now())
        ),
        "project_copyright": getattr(
            settings, "PROJECT_COPYRIGHT", "@2025 Nome do projeto"
        ),
        "project_license": getattr(settings, "PROJECT_LICENSE", "Licença MIT"),
        "project_license_url": getattr(
            settings, "PROJECT_LICENSE_URL", "https://opensource.org/license/mit"
        ),
        "hostname": getattr(settings, "HOSTNAME", "HOSTNAME"),
        "admin_app_list": site_admin_atual.get_app_list(request),
        "available_apps": site_admin_atual.get_app_list(request),
        "dsgovbr": dsgovbr_dict,
    }
