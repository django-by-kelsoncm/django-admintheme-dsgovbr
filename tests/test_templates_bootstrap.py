"""Migração para o Bootstrap 5 com o dsgovbr-bootstraped (issue #24)."""

import re
from pathlib import Path
from types import SimpleNamespace

import pytest
from django import template
from django.conf import settings

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
    "dsgovbr/header.html",
    "dsgovbr/menu.html",
    "admin/app_list.html",
    "admin/change_form.html",
    "admin/change_list.html",
    "admin/change_list_header.html",
    "admin/change_list_dsgovbr_results.html",
    "admin/change_list_object_tools.html",
    "admin/includes/fieldset.html",
    "admin/edit_inline/stacked.html",
    "admin/edit_inline/tabular.html",
    "admin/login.html",
    "admin/pagination.html",
    "admin/search_form.html",
    "admin/submit_line.html",
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


@pytest.mark.parametrize("nome", REESCRITOS)
def test_templates_reescritos_compilam(nome: str) -> None:
    from django.template import Engine

    engine = Engine(
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
    engine.get_template(nome)


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


def test_lista_usa_o_template_de_resultados_do_tema() -> None:
    fonte = (PACOTE / "templatetags" / "dsgovbr_admin_list.py").read_text(
        encoding="utf-8"
    )
    assert 'template_name="change_list_dsgovbr_results.html"' in fonte
