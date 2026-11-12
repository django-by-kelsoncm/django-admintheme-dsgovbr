import pytest
from django.conf import settings
from django.test import RequestFactory, override_settings
from django.urls import path
from dsgovbr.context_processors import layout_settings


# Simple view for testing url resolution
def dummy_view(request):
    return None


urlpatterns = [
    path("logout/", dummy_view, name="logout"),
    path("buscar/", dummy_view, name="site_search"),
    path("buscar/autocomplete/", dummy_view, name="site_index_autocomplete"),
]


@pytest.fixture(autouse=True)
def setup_django():
    # Make sure django settings are configured
    if not settings.configured:
        settings.configure(
            SECRET_KEY="test-secret-key",
            ROOT_URLCONF=__name__,
            PROJECT_COMPANY="Minha empresa",
            PROJECT_TITLE="Nome do projeto",
            PROJECT_SUBTITLE="Slogan do projeto",
            INSTALLED_APPS=[
                "django.contrib.admin",
                "django.contrib.auth",
                "django.contrib.contenttypes",
                "django.contrib.sessions",
                "django.contrib.messages",
            ],
            TEMPLATES=[
                {
                    "BACKEND": "django.template.backends.django.DjangoTemplates",
                    "DIRS": [],
                    "APP_DIRS": True,
                }
            ],
        )
    import django

    django.setup()


@pytest.fixture
def request_with_user():
    from django.contrib.auth.models import AnonymousUser

    rf = RequestFactory()
    request = rf.get("/")
    request.user = AnonymousUser()
    return request


def test_search_not_active(request_with_user):
    with override_settings(DSGOVBR_HEADER={"search": {"ativo": False}}):
        context = layout_settings(request_with_user)
        search_ctx = context["dsgovbr"]["header"]["search"]
        assert search_ctx["ativo"] is False
        assert search_ctx["show"] is False
        assert search_ctx["url"] == ""


def test_search_active_but_no_reverse_match(request_with_user):
    with override_settings(
        ROOT_URLCONF=__name__,
        DSGOVBR_HEADER={"search": {"ativo": True, "view_name": "non_existent_view"}},
    ):
        context = layout_settings(request_with_user)
        search_ctx = context["dsgovbr"]["header"]["search"]
        assert search_ctx["ativo"] is True
        assert search_ctx["show"] is False
        assert search_ctx["url"] == ""


def test_search_active_with_reverse_match(request_with_user):
    with override_settings(
        ROOT_URLCONF=__name__,
        DSGOVBR_HEADER={
            "search": {
                "ativo": True,
                "view_name": "site_search",
                "autocomplete": {"ativo": True, "view_name": "site_index_autocomplete"},
            }
        },
    ):
        context = layout_settings(request_with_user)
        search_ctx = context["dsgovbr"]["header"]["search"]
        assert search_ctx["ativo"] is True
        assert search_ctx["show"] is True
        assert search_ctx["url"] == "/buscar/"

        autocomplete_ctx = search_ctx["autocomplete"]
        assert autocomplete_ctx["ativo"] is True
        assert autocomplete_ctx["show"] is True
        assert autocomplete_ctx["url"] == "/buscar/autocomplete/"


def test_autocomplete_disabled(request_with_user):
    with override_settings(
        ROOT_URLCONF=__name__,
        DSGOVBR_HEADER={
            "search": {
                "ativo": True,
                "view_name": "site_search",
                "autocomplete": {
                    "ativo": False,
                    "view_name": "site_index_autocomplete",
                },
            }
        },
    ):
        context = layout_settings(request_with_user)
        search_ctx = context["dsgovbr"]["header"]["search"]
        assert search_ctx["ativo"] is True
        assert search_ctx["show"] is True

        autocomplete_ctx = search_ctx["autocomplete"]
        assert autocomplete_ctx["ativo"] is False
        assert autocomplete_ctx["show"] is False
        assert autocomplete_ctx["url"] == ""


def test_logout_url_sem_rota_logout(request_with_user):
    from django.urls import NoReverseMatch

    from dsgovbr import context_processors

    def sem_logout(name, *args, **kwargs):
        raise NoReverseMatch(name)

    original = context_processors.reverse
    context_processors.reverse = sem_logout
    try:
        assert context_processors._logout_url() == ""
    finally:
        context_processors.reverse = original


def test_logout_url_com_rota_logout():
    from dsgovbr.context_processors import _logout_url

    assert _logout_url() == "/logout/"


def test_sair_usa_post_na_mesma_aba(request_with_user):
    # LogoutView (Django 5+) recusa GET com 405
    itens = layout_settings(request_with_user)["dsgovbr"]["header"]["login"][
        "dropdown"
    ]["items"]
    sair = next(item for item in itens if item["label"] == "Sair")
    assert sair["method"] == "post"
    assert "target" not in sair


def test_detalhes_de_header_menu_e_rodape_vem_vazios(request_with_user):
    dsgovbr = layout_settings(request_with_user)["dsgovbr"]
    assert dsgovbr["header"]["links"] == {"show": False, "items": []}
    assert dsgovbr["header"]["funcionalidades"] == {"show": False, "items": []}
    assert dsgovbr["header"]["menu"]["footer"] == {
        "logos": [],
        "links": [],
        "redes_sociais": [],
        "licenca": "",
    }
    footer = dsgovbr["footer"]
    assert footer["logo"] is None and footer["assinatura"] is None
    assert footer["colunas"] == [] and footer["redes_sociais"] == []
    assert footer["texto"] == ""


def test_cookiebar_vem_desligado_e_aceita_ajustes(request_with_user):
    cookiebar = layout_settings(request_with_user)["dsgovbr"]["cookiebar"]
    assert cookiebar["show"] is False and cookiebar["grupos"] == []
    grupos = [
        {"nome": "desempenho", "rotulo": "Desempenho", "descricao": "Mede o uso."}
    ]
    with override_settings(DSGOVBR_COOKIEBAR={"show": True, "grupos": grupos}):
        cookiebar = layout_settings(request_with_user)["dsgovbr"]["cookiebar"]
        assert cookiebar["show"] is True and cookiebar["grupos"] == grupos
        assert cookiebar["texto"]  # mantém o texto padrão


def test_project_home_url_respeita_subcaminho(request_with_user):
    from django.urls import get_script_prefix, set_script_prefix

    anterior = get_script_prefix()
    set_script_prefix("/registro/")
    try:
        assert layout_settings(request_with_user)["project_home_url"] == "/registro/"
        with override_settings(PROJECT_HOME_URL="/inicio/"):
            assert layout_settings(request_with_user)["project_home_url"] == "/inicio/"
    finally:
        set_script_prefix(anterior)


def test_sem_avatar_externo_no_contexto(request_with_user):
    assert "user_avatar" not in layout_settings(request_with_user)["dsgovbr"]


def test_seletor_de_modo_ligado_por_padrao(request_with_user):
    modo = layout_settings(request_with_user)["dsgovbr"]["header"]["modo"]
    assert modo == {"show": True, "label": "Modo escuro", "icon": "fas fa-adjust"}


def test_seletor_de_modo_pode_ser_desligado(request_with_user):
    with override_settings(DSGOVBR_HEADER={"modo": {"show": False}}):
        modo = layout_settings(request_with_user)["dsgovbr"]["header"]["modo"]
        assert modo["show"] is False
