import pytest
from django.conf import settings
from django.test import RequestFactory
from dsgovbr import menus


@pytest.fixture(autouse=True)
def setup_django():
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
        )
    import django

    django.setup()


@pytest.fixture
def clean_registry():
    # Salva o estado original do registry e limpa para os testes
    original_folders = menus.registry._folders
    original_reorder_callbacks = menus.registry._reorder_callbacks
    original_global_order = menus.registry._global_order
    original_items_order = menus.registry._items_order

    menus.registry._folders = {}
    menus.registry._reorder_callbacks = []
    menus.registry._global_order = []
    menus.registry._items_order = {}

    yield menus.registry

    # Restaura o estado original
    menus.registry._folders = original_folders
    menus.registry._reorder_callbacks = original_reorder_callbacks
    menus.registry._global_order = original_global_order
    menus.registry._items_order = original_items_order


def test_register_folder(clean_registry):
    folder = menus.register_folder(
        "test_app", name="Test App", icon="fas fa-test", order=10
    )
    assert folder.app_label == "test_app"
    assert folder.name == "Test App"
    assert folder.icon == "fas fa-test"
    assert folder.order == 10


def test_register_item(clean_registry):
    item = menus.register_item(
        "test_app", "Test Item", "/test-url/", icon="fas fa-item", order=5
    )
    assert item.name == "Test Item"
    assert item.url == "/test-url/"
    assert item.icon == "fas fa-item"
    assert item.order == 5

    # Verifica se a pasta correspondente foi criada
    folder = clean_registry._folders["test_app"]
    assert len(folder._items) == 1
    assert folder._items[0] == item


def test_set_order(clean_registry):
    from django.contrib.auth.models import AnonymousUser

    menus.register_folder("app_c", name="App C")
    menus.register_folder("app_a", name="App A")
    menus.register_folder("app_b", name="App B")

    # Registra itens em todas para não serem removidas como vazias
    menus.register_item("app_c", "Item C", "/c/")
    menus.register_item("app_a", "Item A", "/a/")
    menus.register_item("app_b", "Item B", "/b/")

    rf = RequestFactory()
    request = rf.get("/")
    request.user = AnonymousUser()

    # Padrão: sem ordenação global configurada, ordena pelo nome/app_label
    menu_list = menus.get_menu_list(request)
    assert [m["app_label"] for m in menu_list] == ["app_a", "app_b", "app_c"]

    # Configura ordenação específica
    menus.set_order(["app_b", "app_c", "app_a"])
    menu_list = menus.get_menu_list(request)
    assert [m["app_label"] for m in menu_list] == ["app_b", "app_c", "app_a"]


def test_set_items_order(clean_registry):
    from django.contrib.auth.models import AnonymousUser

    menus.register_item("my_app", "Item Z", "/z/")
    menus.register_item("my_app", "Item A", "/a/")
    menus.register_item("my_app", "Item M", "/m/")

    rf = RequestFactory()
    request = rf.get("/")
    request.user = AnonymousUser()

    # Padrão: ordena por nome
    menu_list = menus.get_menu_list(request)
    models = menu_list[0]["models"]
    assert [m["name"] for m in models] == ["Item A", "Item M", "Item Z"]

    # Configura ordenação específica dos itens
    menus.set_items_order("my_app", ["Item M", "Item Z", "Item A"])
    menu_list = menus.get_menu_list(request)
    models = menu_list[0]["models"]
    assert [m["name"] for m in models] == ["Item M", "Item Z", "Item A"]


def test_reorder_callback(clean_registry):
    from django.contrib.auth.models import AnonymousUser

    menus.register_item("app_a", "Item A", "/a/")
    menus.register_item("app_b", "Item B", "/b/")

    def reverse_callback(menu_list):
        return list(reversed(menu_list))

    menus.add_reorder_callback(reverse_callback)

    rf = RequestFactory()
    request = rf.get("/")
    request.user = AnonymousUser()

    menu_list = menus.get_menu_list(request)
    assert [m["app_label"] for m in menu_list] == ["app_b", "app_a"]


def test_item_visibility_and_permissions(clean_registry):
    from django.contrib.auth.models import AnonymousUser, User

    # Item público
    menus.register_item("app_pub", "Public", "/pub/")
    # Item com permissão
    menus.register_item("app_priv", "Private", "/priv/", permission="auth.view_user")

    rf = RequestFactory()

    # Usuário Anônimo
    request_anon = rf.get("/")
    request_anon.user = AnonymousUser()
    menu_list = menus.get_menu_list(request_anon)
    assert len(menu_list) == 1
    assert menu_list[0]["app_label"] == "app_pub"

    # Usuário Autenticado sem permissão
    user_without_perm = User(username="user1")
    request_user = rf.get("/")
    request_user.user = user_without_perm
    # Mock has_perm
    user_without_perm.has_perm = lambda perm: False

    menu_list = menus.get_menu_list(request_user)
    assert len(menu_list) == 1
    assert menu_list[0]["app_label"] == "app_pub"

    # Usuário Autenticado com permissão
    user_with_perm = User(username="user2")
    request_admin = rf.get("/")
    request_admin.user = user_with_perm
    user_with_perm.has_perm = lambda perm: perm == "auth.view_user"

    menu_list = menus.get_menu_list(request_admin)
    assert len(menu_list) == 2
    assert {m["app_label"] for m in menu_list} == {"app_pub", "app_priv"}


def test_full_admin_app_list_nao_recursa_com_site_dsgovbr(monkeypatch):
    from django.contrib import admin

    from dsgovbr.admin import DSGovBrAdminSite

    site = DSGovBrAdminSite()
    monkeypatch.setattr(admin, "site", site)
    request = RequestFactory().get("/")
    assert menus.get_full_admin_app_list(request) == []
