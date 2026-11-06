# Django DSGovBR 🏛️

[![PyPI version](https://badge.fury.io/py/django-dsgovbr.svg)](https://badge.fury.io/py/django-dsgovbr)
[![Python Versions](https://img.shields.io/pypi/pyversions/django-dsgovbr.svg)](https://pypi.org/project/django-dsgovbr/)
[![Django Versions](https://img.shields.io/badge/django-4.2%20%7C%205.0%20%7C%206.0-blue.svg)](https://www.djangoproject.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Pacote Django para integração com o
[Design System do Governo Federal Brasileiro (DS Gov.BR)](https://www.gov.br/ds/home) no Django Admin e formulários
Django.

> 📚 **Documentação Oficial e Suíte**: Para guias completos da suíte e outros temas da organização, acesse [django-adminthemes.github.io](https://django-adminthemes.github.io).

---

## Sobre

O **django-dsgovbr** facilita a implementação do Design System oficial do Governo Federal em projetos Django,
garantindo conformidade visual, acessibilidade (WCAG) e padrão de usabilidade estabelecidos pelo gov.br.

---

## Como Usar

### 1. Instalação via pip

```bash
pip install django-dsgovbr
```

### 2. Configuração no `settings.py`

Troque o `'django.contrib.admin'` pelas apps do tema (o `DSGovBrAdminConfig` é o admin do Django com o site do tema) e
adicione o `compressor`, que compila o SCSS próprio do tema:

```python
INSTALLED_APPS = [
    'dsgovbr.apps.DSGovBRConfig',
    'dsgovbr.apps.DSGovBrAdminConfig',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'compressor',
    # ...
]

TEMPLATES[0]['OPTIONS']['context_processors'] += ['dsgovbr.context_processors.layout_settings']

STATICFILES_FINDERS = [
    'django.contrib.staticfiles.finders.FileSystemFinder',
    'django.contrib.staticfiles.finders.AppDirectoriesFinder',
    'compressor.finders.CompressorFinder',
]
COMPRESS_PRECOMPILERS = (('text/x-scss', 'django_libsass.SassCompiler'),)
```

Em produção com `whitenoise` (ou outro servidor de estáticos que só serve o que existe ao subir), use
`COMPRESS_OFFLINE = True` e gere o CSS no build, depois do `collectstatic`: `python manage.py compress`.

O item "Sair" do usuário usa a rota `logout` do projeto ou, se ela não existir, `admin:logout`.

Detalhes opcionais do header, do menu e do rodapé, como no exemplo "Painel administrativo" do dsgovbr-bootstraped
(todos vazios por padrão; o exemplo completo está em `sandbox/config/settings.py`):

```python
REDES = [{"label": "YouTube", "icon": "fab fa-youtube", "url": "https://www.youtube.com/..."}]

DSGOVBR_HEADER = {
    # em_linha: links e ícones na linha do header a partir de 1200px (dropdown abaixo disso)
    "links": {"show": True, "em_linha": True, "items": [{"label": "Documentação", "url": "/docs/"}]},
    "funcionalidades": {
        "show": True,
        "em_linha": True,
        "items": [{"label": "Suporte", "icon": "fas fa-headset", "url": "/suporte/"}],
    },
    # o dict "menu" substitui o padrão inteiro: repita "show" e "localizacao"
    "menu": {
        "show": True,
        "localizacao": "flutuante",
        "footer": {
            "logos": [{"src": "/static/img/orgao.svg", "alt": "Logo do órgão"}],
            "links": [{"label": "Ajuda", "url": "https://...", "target": "_blank"}],
            "redes_sociais": REDES,
            "licenca": "Conteúdo publicado sob a licença Creative Commons Atribuição 4.0.",
        },
    },
}
DSGOVBR_FOOTER = {
    "logo": {"src": "/static/img/logo-negativo.svg", "alt": "Logo do sistema"},
    "colunas": [{"titulo": "Ajuda", "links": [{"label": "Fale conosco", "url": "/contato/"}]}],
    "redes_sociais": REDES,
    "assinatura": {"src": "/static/img/orgao-negativo.svg", "alt": "Assinatura do órgão"},
    "texto": "Texto antes do copyright.",
}
PROJECT_RELEASES_URL = "https://github.com/org/projeto/releases/tag/"  # + PROJECT_VERSION
```

Para o `DSGovBrModelAdmin` com importação/exportação, instale o extra: `pip install django-dsgovbr[import-export]`.

### 3. Aparência: Bootstrap 5 com o GOV.BR DS

Desde a versão 7.0.0 os templates usam classes do [Bootstrap 5.3](https://getbootstrap.com/docs/5.3/) com o tema
[dsgovbr-bootstraped](https://github.com/abrasileirado/dsgovbr-bootstraped), que dá ao Bootstrap a aparência do
GOV.BR DS. O CSS do tema (v0.10.0) e o `bootstrap.bundle.min.js` (5.3.8) vêm no pacote, em `static/vendors/`; o JS do
GOV.BR DS (`core-init.js`) não é mais carregado.

- **Nos seus templates**: use classes do Bootstrap (`btn btn-primary`, `alert alert-success`, `card`, `form-control`…)
  em vez de `br-*`. Exemplos de cada componente no
  [catálogo do dsgovbr-bootstraped](https://abrasileirado.github.io/dsgovbr-bootstraped/componentes/).
- **Formulários**: o `dsgovbr/js/dsgovbr_forms.js` aplica `.form-control`, `.form-select` e `.form-check-input` aos
  campos do Django, com qualquer `FORM_RENDERER`. Para ignorar um campo ou bloco, use `data-dsgovbr-ignore`.
- **Layout**: segue o exemplo "Painel administrativo" do dsgovbr-bootstraped. Header, conteúdo e rodapé usam
  `container-lg` (`DSGOVBR_HEADER["width_style"]`: `sm`, `md`, `lg`, `xl`, `xxl` ou `fluid`).
- **Menu**: offcanvas aberto pelo botão (`DSGOVBR_HEADER["menu"]["localizacao"] = "flutuante"`, padrão); com `"fixo"`
  fica aberto ao lado do conteúdo a partir de 1200px.
- **Usuário no header**: Sign-in com avatar como o `avatar-dropdown` do GOV.BR DS (avatar, "Olá, **Nome**" e seta).
  Itens de `DSGOVBR_HEADER["login"]["dropdown"]["items"]` com `"method": "post"` viram um formulário com CSRF; o
  "Sair" padrão usa isso, porque o `LogoutView` do Django 5+ recusa GET.
- **Título da página**: o bloco `title_actions` do `dsgovbr/base.html` põe ações à direita do título (na lista: busca,
  filtros, mais opções e "Adicionar").
- **Cookiebar**: o bloco `cookie_consent` do `dsgovbr/base.html` vem vazio; sobrescreva-o com um
  `.offcanvas.offcanvas-bottom` para exibir o aviso.

---

## Desenvolvimento Local (Workspace Privado)

Para contribuir com o projeto e rodar a suíte inteira localmente, utilize o ambiente orquestrado do
**workspace privado** da organização **Django Admin Themes**:

```bash
# 1. Clone o repositório workspace privado
git clone git@github.com:django-adminthemes/workspace.git ~/projetos/PESSOAL/django-adminthemes/workspace
cd ~/projetos/PESSOAL/django-adminthemes/workspace

# 2. Inicialize o ambiente (clona repositórios e configura a CLI)
./dbkw setup

# 3. Suba o container do DSGovBR sandbox
dbkw launch dsgovbr
```

Para mais detalhes sobre os comandos CLI e o ambiente de desenvolvimento, veja a documentação do [workspace/README.md](https://github.com:django-adminthemes/workspace).

---

## 📄 Licença

Distribuído sob a licença MIT. Veja `LICENSE` para mais detalhes.
