"""Configuração do Sphinx para a documentação do django-dsgovbr."""

from __future__ import annotations

import sys
import tomllib
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(RAIZ / "src"))

# O autodoc importa os módulos do app: o Django precisa de settings mínimos.
import django  # noqa: E402
from django.conf import settings  # noqa: E402

if not settings.configured:
    settings.configure(
        SECRET_KEY="sphinx-docs",
        STATIC_URL="/static/",
        STATIC_ROOT=str(RAIZ / "docs" / "_build" / "static"),
        INSTALLED_APPS=[
            "django.contrib.admin",
            "django.contrib.auth",
            "django.contrib.contenttypes",
            "django.contrib.sessions",
            "django.contrib.messages",
        ],
    )
    django.setup()

with (RAIZ / "pyproject.toml").open("rb") as arquivo:
    _PYPROJECT = tomllib.load(arquivo)

project = "django-dsgovbr"
author = "Kelson da Costa Medeiros"
copyright = "2026, django-by-kelsoncm"  # noqa: A001
release = _PYPROJECT["project"]["version"]
language = "pt_BR"

extensions = [
    "sphinx.ext.apidoc",
    "sphinx.ext.autodoc",
    "sphinx.ext.viewcode",
    "sphinx.ext.githubpages",
    "sphinx.ext.napoleon",
    "dsgovbr_sphinx_theme.componentes",
]

# Referência da API gerada a cada build (substitui o sphinx-apidoc do workflow).
apidoc_modules = [
    {
        "path": "../src/dsgovbr",
        "destination": "api",
        "separate_modules": True,
        "module_first": True,
    },
]

# Dependências opcionais do app (extras), dispensáveis para gerar a referência.
autodoc_mock_imports = ["import_export"]

templates_path = ["_templates"]
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]
root_doc = "index"

html_theme = "dsgovbr_sphinx_theme"
html_title = f"{project} {release}"
html_theme_options = {
    "tagline": "Django e Django Admin com visual GOV.BR DS",
    "github_url": "https://github.com/django-by-kelsoncm/django-admintheme-dsgovbr",
    "navigation_links": "PyPI|https://pypi.org/project/django-dsgovbr/",
}
