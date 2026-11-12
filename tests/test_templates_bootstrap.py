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
    "dsgovbr/base.html",
    "dsgovbr/menu.html",
    "dsgovbr/menu_items.html",
    "admin/app_list.html",
    "admin/app_index.html",
    "admin/base.html",
    "admin/index.html",
    "admin/includes/model_cards.html",
    "admin/change_form.html",
    "admin/change_list.html",
    "admin/change_list_dsgovbr_results.html",
    "admin/change_list_object_tools.html",
    "admin/includes/fieldset.html",
    "admin/edit_inline/stacked.html",
    "admin/edit_inline/tabular.html",
    "admin/login.html",
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
        "vendors/dsgovbr-bootstraped/dsgovbr-bootstraped-modo.js",
        "vendors/dsgovbr-bootstraped/dsgovbr-bootstraped-componentes.js",
        "vendors/dsgovbr-bootstraped/dsgovbr-bootstraped-cookies.js",
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


def test_rodape_do_menu_vazio_nao_aparece() -> None:
    html = _render(
        "dsgovbr/menu.html",
        _dsgovbr_menu({"logos": [], "links": [], "redes_sociais": [], "licenca": ""}),
    )
    assert "dsgovbr-menu-rodape" not in html


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
    assert '<dsgovbr-logo src="/l.svg" alt="Logo do órgão"></dsgovbr-logo>' in html
    assert (
        '<dsgovbr-rede href="https://yt.example" icone="fab fa-youtube">YouTube' in html
    )
    assert "<dsgovbr-aviso>Licença CC BY 4.0</dsgovbr-aviso>" in html


def test_header_e_rodape_sao_web_components() -> None:
    base = (TEMPLATES / "dsgovbr" / "base.html").read_text(encoding="utf-8")
    for trecho in (
        "<dsgovbr-header",
        "<dsgovbr-breadcrumb>",
        "<dsgovbr-acoes>",
        "{% block title_actions %}",
        "{% block breadcrumb %}",
        "<dsgovbr-usuario-menu>",
        "<dsgovbr-acesso-rapido>",
        "<dsgovbr-funcionalidades>",
        "<dsgovbr-footer",
        "<dsgovbr-coluna",
        "<dsgovbr-rede ",
        "rodape.logo",
        "rodape.colunas",
        "rodape.redes_sociais",
        "rodape.assinatura",
        "rodape.texto",
    ):
        assert trecho in base, trecho


def test_sair_do_header_envia_post_com_csrf() -> None:
    base = (TEMPLATES / "dsgovbr" / "base.html").read_text(encoding="utf-8")
    assert "{% if item.method == 'post' %}" in base
    assert (
        '<form method="post" action="{{ item.url }}" data-dsgovbr-link-post hidden>'
        in base
    )
    assert "{% csrf_token %}" in base
    js = (PACOTE / "static" / "dsgovbr" / "js" / "dsgovbr_componentes.js").read_text(
        encoding="utf-8"
    )
    assert "form[data-dsgovbr-link-post]" in js


def _changelist(**atributos) -> SimpleNamespace:
    padrao = {
        "get_query_string": lambda params=None, remove=None: "?"
        + "&".join(f"{k}={v}" for k, v in (params or {}).items()),
        "can_show_all": True,
        "show_all": False,
        "multi_page": True,
    }
    return SimpleNamespace(**{**padrao, **atributos})


def test_pagina_href_tem_o_marcador_do_componente() -> None:
    from dsgovbr.templatetags.dsgovbr_admin_list import dsgovbr_pagina_href

    assert dsgovbr_pagina_href(_changelist()) == "?p={pagina}"


def test_mostrar_todos_so_aparece_quando_ha_o_que_mostrar() -> None:
    from dsgovbr.templatetags.dsgovbr_admin_list import dsgovbr_mostrar_todos_href

    assert dsgovbr_mostrar_todos_href(_changelist()) == "?all="
    assert dsgovbr_mostrar_todos_href(_changelist(show_all=True)) == ""
    assert dsgovbr_mostrar_todos_href(_changelist(multi_page=False)) == ""
    assert dsgovbr_mostrar_todos_href(_changelist(can_show_all=False)) == ""


def test_filtros_do_changelist_viram_opcoes_com_os_parametros_da_opcao() -> None:
    from dsgovbr.templatetags.dsgovbr_admin_list import dsgovbr_filtros

    class Spec:
        title = "data de criação"

        def expected_parameters(self):
            return ["criado__gte", "criado__lt"]

        def choices(self, cl):
            yield {"selected": True, "query_string": "?q=x", "display": "Todas"}
            yield {
                "selected": False,
                "query_string": "?q=x&criado__gte=2026-11-01&criado__lt=2026-12-01&o=1",
                "display": "Este mês",
            }

    resultado = dsgovbr_filtros(_changelist(filter_specs=[Spec()]))
    assert resultado["parametros"] == ["criado__gte", "criado__lt"]
    (filtro,) = resultado["filtros"]
    assert filtro["nome"] == "filtro-1" and filtro["rotulo"] == "Data de criação"
    # "Todas" não entra; da opção só os parâmetros do filtro (sem q nem o)
    assert filtro["opcoes"] == [
        {
            "valor": "criado__gte=2026-11-01&criado__lt=2026-12-01",
            "texto": "Este mês",
            "selecionada": False,
        }
    ]


def test_lista_usa_dsgovbr_tabela_com_post_e_selecao_do_django() -> None:
    html = (TEMPLATES / "admin" / "change_list.html").read_text(encoding="utf-8")
    assert '<form id="changelist-form" method="post"' in html
    assert "{% csrf_token %}" in html
    for trecho in (
        "<dsgovbr-tabela",
        'selecao-nome="_selected_action"',
        "paginacao-href",
        "<dsgovbr-filtro",
        "<dsgovbr-opcao",
        "<dsgovbr-lote-acao",
        'name="action"',
        'name="index"',
    ):
        assert trecho in html, trecho
    resultados = (TEMPLATES / "admin" / "change_list_dsgovbr_results.html").read_text(
        encoding="utf-8"
    )
    assert '<tr data-valor="{{ result.pk }}">' in resultados


def test_cola_js_cobre_busca_filtros_e_acoes_em_lote() -> None:
    js = (PACOTE / "static" / "dsgovbr" / "js" / "dsgovbr_componentes.js").read_text(
        encoding="utf-8"
    )
    for trecho in (
        "data-busca-acao",
        "dsgovbr:tabela-acao",
        "form[data-tabela-consulta]",
        "data-filtro-parametros",
        "CAMINHO_LOCAL.test(acao)",
        "CAMINHO_LOCAL.test(sugestoes)",
    ):
        assert trecho in js, trecho


def test_base_carrega_web_components_e_cola_com_defer() -> None:
    base = (TEMPLATES / "dsgovbr" / "base.html").read_text(encoding="utf-8")
    head = base.split("</head>")[0]
    assert re.search(r"<script[^>]*dsgovbr-bootstraped-componentes\.js[^>]*defer", head)
    # a API de cookies é síncrona; o cookiebar só com DSGOVBR_COOKIEBAR
    assert "{% if dsgovbr.cookiebar.show %}" in head
    assert not re.search(r"<script[^>]*bootstraped-cookies[^>]*(defer|async)", head)
    assert re.search(
        r"<script[^>]*dsgovbr_componentes\.js[^>]*defer", base
    ), "a cola roda depois da montagem dos componentes"
    assert "<dsgovbr-cookiebar" in base


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


def test_botao_do_menu_some_sem_menu_na_pagina() -> None:
    scss = (PACOTE / "static" / "dsgovbr" / "scss" / "dsgovbr.scss").read_text(
        encoding="utf-8"
    )
    assert (
        'body:not(:has(#main-navigation)) dsgovbr-header [data-bs-target="#main-navigation"]'
        in scss
    )


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
    # Select2 simples vazio (linha nova de inline) não colapsa (issue #35)
    assert re.search(
        r"select2-selection--single \.select2-selection__rendered \{[^}]*min-height: 1\.5em",
        css,
    )
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


# Modo escuro (issue #37): componentes com cor fixa do modo claro no vendor.
@pytest.mark.parametrize(
    "seletor, propriedade",
    [
        (".navbar", "--bs-navbar-color"),
        (".navbar", "--bs-navbar-brand-color"),
        ('.navbar [role="search"] .form-control', "background-color"),
        (".breadcrumb", "--bs-breadcrumb-item-active-color"),
        (".form-control", "color"),
        (".form-select", "color"),
        (".btn-outline-primary", "--bs-btn-color"),
        (".btn-outline-secondary", "--bs-btn-color"),
        (".pagination", "--bs-pagination-color"),
        (".list-group", "--bs-list-group-action-color"),
        (".dropdown-menu", "--bs-dropdown-link-color"),
    ],
)
def test_modo_escuro_troca_cores_fixas_por_variaveis(
    seletor: str, propriedade: str
) -> None:
    css = _scss_compilado()
    regras = re.findall(
        r'\[data-bs-theme="dark"\] ' + re.escape(seletor) + r"[^{]*\{([^}]*)\}", css
    )
    valores = [
        valor.strip()
        for regra in regras
        for nome, valor in re.findall(r"([-\w]+)\s*:\s*([^;]+)", regra)
        if nome == propriedade
    ]
    assert valores, (seletor, propriedade)
    assert all(valor.startswith("var(--bs-") for valor in valores), valores


def test_modo_escuro_respeita_dropdown_com_tema_claro_proprio() -> None:
    css = _scss_compilado()
    assert '[data-bs-theme="dark"] .dropdown-menu:not([data-bs-theme="light"])' in css


def test_calendario_e_relogio_abrem_abaixo_do_link() -> None:
    css = _scss_compilado()
    assert re.search(r"\.calendarbox,\s*\.clockbox \{[^}]*margin-top: 0\.25rem", css)
    js = (PACOTE / "static" / "dsgovbr" / "js" / "dsgovbr_forms.js").read_text(
        encoding="utf-8"
    )
    assert "atalhos.openCalendar = function" in js
    assert "atalhos.openClock = function" in js
    assert "ancora.bottom + window.scrollY" in js


def test_seletor_de_modo_no_header_e_script_no_head() -> None:
    """Issue #41: botão de modo claro/escuro com o JS do dsgovbr-bootstraped."""
    base = (TEMPLATES / "dsgovbr" / "base.html").read_text(encoding="utf-8")
    head = base.split("</head>")[0]
    script = "vendors/dsgovbr-bootstraped/dsgovbr-bootstraped-modo.js"
    assert script in head
    # síncrono e depois do CSS, para aplicar o modo antes da primeira pintura
    assert head.index("dsgovbr-bootstraped.min.css") < head.index(script)
    assert not re.search(r"<script[^>]*(defer|async)[^>]*bootstraped-modo", head)
    assert "{% if dsgovbr.header.modo.show %}" in head

    # o botão é desenhado pelo <dsgovbr-header modo>
    assert "{% if cab.modo.show %}modo{% endif %}" in base

    js = (
        PACOTE
        / "static"
        / "vendors"
        / "dsgovbr-bootstraped"
        / "dsgovbr-bootstraped-modo.js"
    ).read_text(encoding="utf-8")
    assert "[data-dsgovbr-modo]" in js
    assert "dsgovbr-bootstraped:modo" in js
