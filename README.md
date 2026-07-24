# Django DSGovBR 🏛️

[![PyPI version](https://badge.fury.io/py/django-dsgovbr.svg)](https://badge.fury.io/py/django-dsgovbr)
[![Python Versions](https://img.shields.io/pypi/pyversions/django-dsgovbr.svg)](https://pypi.org/project/django-dsgovbr/)
[![Django Versions](https://img.shields.io/badge/django-4.2%20%7C%205.0%20%7C%206.0-blue.svg)](https://www.djangoproject.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Pacote Django para integração com o [Design System do Governo Federal Brasileiro (DS Gov.BR)](https://www.gov.br/ds/home) no Django Admin e formulários Django.

> 📚 **Documentação Oficial e Suíte**: Para guias completos da suíte e outros temas da organização, acesse [django-adminthemes.github.io](https://django-adminthemes.github.io).

---

## Sobre

O **django-dsgovbr** facilita a implementação do Design System oficial do Governo Federal em projetos Django, garantindo conformidade visual, acessibilidade (WCAG) e padrão de usabilidade estabelecidos pelo gov.br.

---

## Como Usar

### 1. Instalação via pip

```bash
pip install django-dsgovbr
```

### 2. Configuração no `settings.py`

Adicione `'dsgovbr'` ao seu `INSTALLED_APPS` **antes** de `'django.contrib.admin'`:

```python
INSTALLED_APPS = [
    'dsgovbr',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # ...
]
```

---

## Desenvolvimento Local (Workspace Privado)

Para contribuir com o projeto e rodar a suíte inteira localmente, utilize o ambiente orquestrado do **workspace privado** da organização **Django Admin Themes**:

```bash
# 1. Clone o repositório workspace privado
git clone git@github.com:django-adminthemes/workspace.git ~/projetos/PESSOAL/django-adminthemes/workspace
cd ~/projetos/PESSOAL/django-adminthemes/workspace

# 2. Inicialize o ambiente (clona repositórios e configura a CLI)
./datw setup

# 3. Suba o container do DSGovBR sandbox
datw launch dsgovbr
```

Para mais detalhes sobre os comandos CLI e o ambiente de desenvolvimento, veja a documentação do [workspace/README.md](https://github.com:django-adminthemes/workspace).

---

## 📄 Licença

Distribuído sob a licença MIT. Veja `LICENSE` para mais detalhes.
