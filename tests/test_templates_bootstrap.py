"""Migração para o Bootstrap 5 com o dsgovbr-bootstraped (issue #24)."""

import re
from pathlib import Path
from types import SimpleNamespace

import pytest
from django import template
from django.conf import settings
from django.contrib import admin

RAIZ = Path(__file__).resolve().parent.parent
PACOTE = RAIZ / "src" / "dsgovbr"
TEMPLATES = PACOTE / "templates"
SANDBOX = RAIZ / "sandbox"

# classes do GOV.BR DS (br-*) e utilitários do Bootstrap 4 que o GOV.BR DS usa
CLASSE_GOVBR = re.compile(r'class="[^"]*(?<![\w-])br-[a-z]')
UTILITARIO_BS4 = re.compile(
    r'class="[^"]*(?<![\w-])(?:mr|ml|pl|pr)-(?:\d|auto)'
    r'|class="[^"]*(?<![\w-])(?:text-right|text-left|sr-only|float-right|float-left)\b'
)

# templates reescritos na migração; precisam compilar com as tags do tema
REESCRITOS = [
    "dsgovbr/avatar.html",
    "dsgovbr/base.html",
    "dsgovbr/header.html",
    "dsgovbr/menu.html",
    "dsgovbr/redes_sociais.html",
    "admin/app_list.html",
    "admin/app_index.html",
    "admin/base.html",
    "admin/index.html",
    "admin/includes/model_cards.html",
    "admin/change_form.html",
    "admin/change_list.html",
    "admin/change_list_header.html",
    "admin/change_list_tools.html",
    "admin/change_list_dsgovbr_results.html",
    "admin/change_list_object_tools.html",
    "admin/includes/fieldset.html",
    "admin/edit_inline/stacked.html",
    "admin/edit_inline/tabular.html",
    "admin/login.html",
    "admin/pagination.html",
    "admin/search_form.html",
    "admin/submit_line.html",
    "admin/widgets/related_widget_wrapper.html",
    "registration/logged_out.html",
    "registration/password_reset_complete.html",
    "registration/password_reset_confirm.html",
    "registration/password_reset_done.html",
    "registration/password_reset_form.html",
]


# {% compress %} sem o django-compressor (que exige STATIC_ROOT): só renderiza o conteúdo
register = template.Library()


class _CompressNode(template.Node):
    def __init__(self, nodelist: template.NodeList) -> None:
        self.nodelist = nodelist

    def render(self, context: template.Context) -> str:
        return self.nodelist.render(context)


@register.tag
def compress(parser: template.base.Parser, token: template.base.Token) -> _CompressNode:
    nodelist = parser.parse(("endcompress",))
    parser.delete_first_token()
    return _CompressNode(nodelist)


@pytest.fixture(autouse=True)
def setup_django():
    if not settings.configured:
        settings.configure(
            SECRET_KEY="test-secret-key",
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


def _htmls(*pastas: Path) -> list[Path]:
    return [
        p
        for pasta in pastas
        for p in pasta.rglob("*.html")
        if "static_root" not in p.parts
    ]


@pytest.mark.parametrize(
    "regra", [CLASSE_GOVBR, UTILITARIO_BS4], ids=["br-*", "bootstrap-4"]
)
def test_templates_sem_classes_do_govbr_ds(regra: re.Pattern) -> None:
    achados = [
        f"{p.relative_to(RAIZ)}:{n}"
        for p in _htmls(TEMPLATES, SANDBOX)
        for n, linha in enumerate(p.read_text(encoding="utf-8").splitlines(), 1)
        if regra.search(linha)
    ]
    assert achados == []


def test_base_carrega_bootstrap_e_nao_o_js_do_govbr_ds() -> None:
    base = (TEMPLATES / "dsgovbr" / "base.html").read_text(encoding="utf-8")
    assert "vendors/dsgovbr-bootstraped/dsgovbr-bootstraped.min.css" in base
    assert "vendors/bootstrap/bootstrap.bundle.min.js" in base
    assert "dsgovbr/js/dsgovbr_forms.js" in base
    assert "core-init.js" not in base
    assert "vendors/serpro/core" not in (
        PACOTE / "static" / "dsgovbr" / "scss" / "dsgovbr.scss"
    ).read_text(encoding="utf-8")


@pytest.mark.parametrize(
    "arquivo",
    [
        "vendors/dsgovbr-bootstraped/dsgovbr-bootstraped.min.css",
        "vendors/dsgovbr-bootstraped/LICENSE",
        "vendors/bootstrap/bootstrap.bundle.min.js",
        "vendors/bootstrap/bootstrap.bundle.min.js.map",
        "vendors/bootstrap/LICENSE",
    ],
)
def test_assets_vendorizados(arquivo: str) -> None:
    assert (PACOTE / "static" / arquivo).is_file()


def test_versao_do_bootstrap_vendorizado() -> None:
    js = (
        PACOTE / "static" / "vendors" / "bootstrap" / "bootstrap.bundle.min.js"
    ).read_text(encoding="utf-8")
    css = (
        PACOTE
        / "static"
        / "vendors"
        / "dsgovbr-bootstraped"
        / "dsgovbr-bootstraped.min.css"
    ).read_text(encoding="utf-8-sig")
    assert "Bootstrap v5.3.8" in js
    assert "Bootstrap  v5.3.8" in css


def _engine():
    from django.template import Engine

    return Engine(
        dirs=[str(TEMPLATES)],
        libraries={
            "admin_list": "django.contrib.admin.templatetags.admin_list",
            "admin_modify": "django.contrib.admin.templatetags.admin_modify",
            "admin_urls": "django.contrib.admin.templatetags.admin_urls",
            "compress": __name__,
            "dsgovbr": "dsgovbr.templatetags.dsgovbr",
            "dsgovbr_admin_list": "dsgovbr.templatetags.dsgovbr_admin_list",
            "i18n": "django.templatetags.i18n",
            "static": "django.templatetags.static",
        },
    )


@pytest.mark.parametrize("nome", REESCRITOS)
def test_templates_reescritos_compilam(nome: str) -> None:
    _engine().get_template(nome)


REDES = [{"label": "YouTube", "icon": "fab fa-youtube", "url": "https://yt.example"}]


def _render(nome: str, contexto: dict) -> str:
    from django.template import Context

    return _engine().get_template(nome).render(Context(contexto))


def _dsgovbr_menu(footer: dict) -> dict:
    return {
        "dsgovbr": {
            "header": {
                "logo": {"show": False},
                "titulo": {"label": "T"},
                "menu": {"localizacao": "flutuante", "footer": footer},
            }
        },
        "available_apps": [],
    }


def test_redes_sociais_renderiza_botoes_acessiveis() -> None:
    html = _render("dsgovbr/redes_sociais.html", {"redes": REDES})
    assert 'href="https://yt.example"' in html
    assert 'aria-label="YouTube"' in html
    assert 'class="fab fa-youtube"' in html


def test_rodape_do_menu_vazio_nao_aparece() -> None:
    html = _render(
        "dsgovbr/menu.html",
        _dsgovbr_menu({"logos": [], "links": [], "redes_sociais": [], "licenca": ""}),
    )
    assert "mt-auto" not in html


def test_rodape_do_menu_com_logos_redes_e_licenca() -> None:
    html = _render(
        "dsgovbr/menu.html",
        _dsgovbr_menu(
            {
                "logos": [{"src": "/l.svg", "alt": "Logo do órgão"}],
                "redes_sociais": REDES,
                "licenca": "Licença CC BY 4.0",
            }
        ),
    )
    assert '<img src="/l.svg" height="33" alt="Logo do órgão">' in html
    assert 'aria-label="YouTube"' in html
    assert "Licença CC BY 4.0" in html


def test_header_e_rodape_tem_os_novos_parametros() -> None:
    header = (TEMPLATES / "dsgovbr" / "header.html").read_text(encoding="utf-8")
    assert header.count("d-none d-xl-flex") == 2
    assert "dsgovbr.header.links.em_linha" in header
    assert "dsgovbr.header.funcionalidades.em_linha" in header
    base = (TEMPLATES / "dsgovbr" / "base.html").read_text(encoding="utf-8")
    for chave in (
        "rodape.logo",
        "rodape.colunas",
        "rodape.redes_sociais",
        "rodape.assinatura",
        "dsgovbr.footer.texto",
    ):
        assert chave in base


def _changelist(pagina_atual: int) -> SimpleNamespace:
    from django.core.paginator import Paginator

    return SimpleNamespace(
        paginator=SimpleNamespace(ELLIPSIS=Paginator.ELLIPSIS),
        page_num=pagina_atual,
        get_query_string=lambda params: "?"
        + "&".join(f"{k}={v}" for k, v in params.items()),
    )


def test_page_item_gera_paginacao_do_bootstrap() -> None:
    from dsgovbr.templatetags.dsgovbr import page_item

    cl = _changelist(pagina_atual=2)
    assert (
        page_item(cl, 3)
        == '<li class="page-item"><a class="page-link" href="?p=3">3</a></li>'
    )
    assert page_item(cl, 2) == (
        '<li class="page-item active" aria-current="page"><span class="page-link">2</span></li>'
    )
    assert page_item(cl, cl.paginator.ELLIPSIS) == (
        '<li class="page-item disabled"><span class="page-link">…</span></li>'
    )


def test_page_item_escapa_a_url() -> None:
    from dsgovbr.templatetags.dsgovbr import page_item

    cl = _changelist(pagina_atual=1)
    cl.get_query_string = lambda params: '?q="><script>'
    assert "<script>" not in page_item(cl, 2)


def test_sair_do_header_envia_post_com_csrf() -> None:
    header = (TEMPLATES / "dsgovbr" / "header.html").read_text(encoding="utf-8")
    assert "{% if item.method == 'post' %}" in header
    assert '<form method="post" action="{{ item.url }}">' in header
    assert "{% csrf_token %}" in header


def test_lista_usa_o_template_de_resultados_do_tema() -> None:
    fonte = (PACOTE / "templatetags" / "dsgovbr_admin_list.py").read_text(
        encoding="utf-8"
    )
    assert 'template_name="change_list_dsgovbr_results.html"' in fonte


def _app(models: list[dict]) -> dict:
    return {"app": {"models": models}, "request": SimpleNamespace(path="/admin/")}


def test_cards_dos_models_com_icone_e_acoes() -> None:
    html = _render(
        "admin/includes/model_cards.html",
        _app(
            [
                {
                    "name": "Notícias",
                    "object_name": "Noticia",
                    "icon": "fas fa-newspaper",
                    "admin_url": "/admin/editorial/noticia/",
                    "add_url": "/admin/editorial/noticia/add/",
                }
            ]
        ),
    )
    assert 'class="card h-100 model-noticia"' in html
    assert 'class="fas fa-newspaper fs-4 text-primary"' in html
    assert 'href="/admin/editorial/noticia/add/"' in html


def test_card_sem_icone_usa_o_padrao_e_sem_add_nao_mostra_adicionar() -> None:
    html = _render(
        "admin/includes/model_cards.html",
        _app(
            [
                {
                    "name": "Tags",
                    "object_name": "Tag",
                    "admin_url": "/t/",
                    "view_only": True,
                }
            ]
        ),
    )
    assert 'class="fas fa-table fs-4 text-primary"' in html
    assert "fa-plus" not in html


def test_breadcrumb_do_admin_nao_usa_o_bloco_breadcrumbs_do_django() -> None:
    for pasta in (TEMPLATES / "admin", TEMPLATES / "simple_history"):
        for arquivo in pasta.rglob("*.html"):
            assert "{% block breadcrumbs %}" not in arquivo.read_text(
                encoding="utf-8"
            ), arquivo
    base = (TEMPLATES / "admin" / "base.html").read_text(encoding="utf-8")
    assert "{% block breadcrumb_home_url %}{% url 'admin:index' %}" in base


def test_nenhum_template_aponta_para_a_raiz_fixa() -> None:
    for arquivo in TEMPLATES.rglob("*.html"):
        assert 'href="/"' not in arquivo.read_text(encoding="utf-8"), arquivo


def test_licenca_sem_url_nao_gera_link_vazio() -> None:
    base = (TEMPLATES / "dsgovbr" / "base.html").read_text(encoding="utf-8")
    assert '{% if project_license_url %}<a href="{{ project_license_url }}"' in base


def _avatar(login: dict, user: object) -> str:
    return _render(
        "dsgovbr/avatar.html", {"dsgovbr": {"header": {"login": login}}, "user": user}
    )


def test_avatar_fotografico_usa_a_foto_padrao_configurada() -> None:
    sem_foto = SimpleNamespace(avatar_url="", get_username=lambda: "ana")
    html = _avatar(
        {"type": "fotografico", "default_avatar_url": "/padrao.png"}, sem_foto
    )
    assert '<img src="/padrao.png" alt="">' in html
    html = _avatar({"type": "fotografico", "default_avatar_url": ""}, sem_foto)
    assert "fa-user" in html


def test_botao_do_menu_some_sem_menu_na_pagina() -> None:
    scss = (PACOTE / "static" / "dsgovbr" / "scss" / "dsgovbr.scss").read_text(
        encoding="utf-8"
    )
    assert "body:not(:has(#main-navigation)) #navigation" in scss


# Widgets do admin sem o base.css do Django (issue #33)
ADMIN_CSS = Path(admin.__file__).resolve().parent / "static" / "admin" / "css"
SCSS = PACOTE / "static" / "dsgovbr" / "scss" / "dsgovbr.scss"


def _scss_compilado() -> str:
    import sass

    return sass.compile(filename=str(SCSS))


def test_related_widget_wrapper_tem_o_wrapper_e_os_popups() -> None:
    html = _render(
        "admin/widgets/related_widget_wrapper.html",
        {
            "rendered_widget": '<select name="orgao"></select>',
            "name": "orgao",
            "model": "órgão",
            "model_name": "orgao",
            "url_params": "_to_field=id&_popup=1",
            "view_related_url_params": "_to_field=id",
            "change_related_template_url": "/admin/c/orgao/__fk__/change/",
            "delete_related_template_url": "/admin/c/orgao/__fk__/delete/",
            "add_related_url": "/admin/c/orgao/add/",
            "can_change_related": True,
            "can_add_related": True,
            "can_delete_related": True,
            "can_view_related": True,
        },
    )
    assert '<div class="related-widget-wrapper" data-model-ref="orgao">' in html
    assert html.count('data-popup="yes"') == 3
    for link in ("change_id_orgao", "add_id_orgao", "delete_id_orgao", "view_id_orgao"):
        assert f'id="{link}"' in html


@pytest.mark.parametrize("arquivo", ["autocomplete.css", "widgets.css"])
def test_variaveis_do_admin_usadas_nos_widgets_sao_definidas(arquivo: str) -> None:
    usadas = set(
        re.findall(r"var\((--[a-z0-9-]+)", (ADMIN_CSS / arquivo).read_text("utf-8"))
    )
    definidas = set(re.findall(r"(--[a-z0-9-]+)\s*:", _scss_compilado()))
    assert usadas, arquivo
    assert usadas <= definidas, sorted(usadas - definidas)


def test_select2_do_admin_usa_o_tema_dsgovbr() -> None:
    css = _scss_compilado()
    assert ".select2-container.select2-container--dsgovbr.select2" in css
    assert "width: 100% !important" in css
    js = (PACOTE / "static" / "dsgovbr" / "js" / "dsgovbr_forms.js").read_text(
        encoding="utf-8"
    )
    assert "'data-theme', 'dsgovbr'" in js
    assert "select.admin-autocomplete" in js


def test_scss_sem_cor_literal_fora_de_variavel() -> None:
    for linha in SCSS.read_text(encoding="utf-8").splitlines():
        codigo = linha.split("//")[0]
        if re.search(r"#[0-9a-fA-F]{3,8}\b|rgba?\(", codigo):
            assert codigo.lstrip().startswith("$"), linha
