
Django DSGovBR
==============


.. image:: https://badge.fury.io/py/django-dsgovbr.svg
   :target: https://badge.fury.io/py/django-dsgovbr
   :alt: PyPI version


.. image:: https://img.shields.io/pypi/pyversions/django-dsgovbr.svg
   :target: https://pypi.org/project/django-dsgovbr/
   :alt: Python Versions


.. image:: https://img.shields.io/badge/django-5.2-blue.svg
   :target: https://www.djangoproject.com/
   :alt: Django Versions


.. image:: https://img.shields.io/badge/License-MIT-yellow.svg
   :target: https://opensource.org/licenses/MIT
   :alt: License: MIT


Pacote Django para adoção do `Design System do Governo Federal Brasileiro (DS Gov.BR) <https://www.gov.br/ds/home>`_ em
sites e painel de administração Django.

.. note::
   🌐 **Documentação Oficial e Suíte**: Para tutoriais unificados e outros temas da organização, acesse `django-adminthemes.github.io <https://django-adminthemes.github.io>`_.
   🛠️ **Desenvolvimento Local**: Contribuições utilizam o `workspace privado <https://github.com/django-adminthemes/workspace>`_ da organização com a CLI ``dbkw``.

📋 Sobre
--------

O **django-dsgovbr** facilita a implementação do Design System oficial do Governo Federal em projetos Django,
inclusive no Django Admin, garantindo conformidade visual e de usabilidade com os padrões estabelecidos pelo gov.br.

🎨 Design System Gov.BR
^^^^^^^^^^^^^^^^^^^^^^^

O `DS Gov.BR <https://www.gov.br/ds/home>`_ é o design system oficial do Governo Federal Brasileiro, criado para
padronizar a experiência do usuário em todos os portais e sistemas governamentais.

**Links Oficiais:**


* 🏠 `Site Oficial <https://www.gov.br/ds/home>`_
* 📚 `Documentação <https://www.gov.br/ds/fundamentos-visuais/visao-geral>`_
* 🎨 `Fundamentos Visuais <https://www.gov.br/ds/fundamentos-visuais/introducao>`_
* 🧩 `Componentes <https://www.gov.br/ds/componentes/overview>`_
* 📐 `Padrões <https://www.gov.br/ds/padroes/introducao>`_
* 💾 `Download dos Assets <https://www.gov.br/ds/recursos/downloads>`_

✨ Recursos Visuais do DS Gov.BR
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

O Design System inclui:

Partes principais
~~~~~~~~~~~~~~~~~


* **Header**\ : Cabeçalho da página
* **Content**\ : Área principal do conteúdo
* **Footer**\ : Rodapé da página (opcional).

Componentes principais
~~~~~~~~~~~~~~~~~~~~~~


* **Formulários**\ : Inputs, selects, checkboxes, radio buttons estilizados
* **Botões**\ : Primários, secundários, terciários com estados hover/active/disabled
* **Mensagens**\ : Alertas, notificações e mensagens de sistema
* **Navegação**\ : Headers, breadcrumbs, menus e abas
* **Tabelas**\ : Grades de dados responsivas e acessíveis
* **Cards**\ : Cartões informativos e de conteúdo
* **Modal**\ : Diálogos e janelas modais
* **Paginação**\ : Controles de navegação entre páginas

Características visuais
~~~~~~~~~~~~~~~~~~~~~~~


* 🎨 **Paleta de Cores Oficial**\ : Azul Gov.BR (#071D41), cores de status e feedbacks
* 📱 **Design Responsivo**\ : Mobile-first, adaptável a todos os dispositivos
* ♿ **Acessibilidade**\ : WCAG 2.1 nível AA, suporte a leitores de tela
* 🔤 **Tipografia Rawline**\ : Fonte oficial do governo federal
* 📐 **Grid System**\ : Sistema de grid consistente (12 colunas)
* 🖼️ **Ícones**\ : Biblioteca Font Awesome 5.12 com ícones customizados

Visual do DS Gov.BR
^^^^^^^^^^^^^^^^^^^

O design é divido em 3 partes principais: Header, Content e Footer (opcional).

.. note::

   As figuras desta seção (Header e Menu) são os diagramas da **especificação do GOV.BR DS**, com a numeração dos
   elementos das tabelas; não são capturas do tema. O tema usa os web components do dsgovbr-bootstrapped, que
   implementam a variante **padrão** do Header (não há a compacta) e o Menu **flutuante** (não há o menu fixo).

Header
~~~~~~

O Header pode ser do tipo padrão ou compacto. O Padrão tem 2 linhas de elementos e o Compacto tem apenas 1 ou
linha de elementos. A anatomia do Header é composta por:

.. list-table::
   :header-rows: 1

   * - #
     - Elemento
     - Padrão
     - Compacto
   * - 1
     - Logo
     - Recomendado
     - Opcional
   * - 2
     - Assinatura
     - Opcional
     - Ausente
   * - 3
     - Título
     - Obrigatório
     - Obrigatório
   * - 4
     - Subtítulo
     - Opcional
     - Opcional
   * - 5
     - Botão Menu
     - Recomendado
     - Opcional
   * - 6
     - Área para links
     - Opcional
     - Opcional
   * - 7
     - Área para funcionalidades
     - Opcional
     - Opcional
   * - 8
     - Botão autenticar
     - Opcional
     - Opcional
   * - 9
     - Avatar do Usuário
     - Opcional
     - Opcional
   * - 10
     - Campo de Busca
     - Opcional
     - Opcional
   * - 11
     - Lista Dropdown
     - Recomendado
     - Opcional
   * - 12
     - Superfície
     - Obrigatório
     - Obrigatório
   * - 13
     - Separadores
     - Obrigatório
     - Obrigatório


Header Padrão
"""""""""""""


.. image:: ./images/header-padrao.png
   :target: ./images/header-padrao.png
   :alt: header-padrao.png


Header Compacto
"""""""""""""""

Especificação do GOV.BR DS; o ``<dsgovbr-header>`` não tem a variante compacta.


.. image:: ./images/header-compacto.png
   :target: ./images/header-compacto.png
   :alt: header-padrao.png


Header Mobile inicial
"""""""""""""""""""""


.. image:: ./images/header-mobile-inicial.png
   :target: ./images/header-mobile-inicial.png
   :alt: header-mobile-inicial.png


Header Mobile ao clicar em search
"""""""""""""""""""""""""""""""""


.. image:: ./images/header-mobile-search.png
   :target: ./images/header-mobile-search.png
   :alt: header-mobile-search.png


Header Mobile nos botões agrupadores de ações (links ou funcionalidades)
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""


.. image:: ./images/header-mobile-actions.png
   :target: ./images/header-mobile-actions.png
   :alt: header-mobile-actions.png


Header Menu
"""""""""""

O Menu é o ``<dsgovbr-menu>``, um offcanvas que flutua sobre o conteúdo (a partir da 8.0.0 não há mais o menu
fixo) e é constituído por:

.. list-table::
   :header-rows: 1

   * - ID
     - Nome
     - Referência
     - Uso
   * - 1
     - Ícone de acionamento
     - Button
     - Opcional
   * - 2
     - Superfície scrim
     - —
     - Condicional
   * - 3
     - Cabeçalho do menu
     - Header
     - Opcional
   * - 4
     - Botão Fechar
     - Button
     - Opcional
   * - 5
     - Item de 1º nível
     - Item
     - Opcional
   * - 6
     - Item de 2º nível
     - Item
     - Condicional
   * - 7
     - Ícone Expandir/Retrair
     - Button
     - Condicional
   * - 8
     - Ícone representativo do item
     - Iconografia
     - Opcional
   * - 9
     - Ícone Acessar Subitens
     - Button
     - Condicional
   * - 10
     - Componente divider
     - Divider
     - Condicional
   * - 11
     - Painel do menu
     - —
     - Obrigatório
   * - 12
     - Rodapé do menu
     - Footer
     - Opcional



.. image:: ./images/header-menu.png
   :target: ./images/header-menu.png
   :alt: header-menu.png



.. image:: ./images/header-menu-flutuante.png
   :target: ./images/header-menu-flutuante.png
   :alt: header-menu-flutuante.png



Especificação do GOV.BR DS para o menu fixo (o ``<dsgovbr-menu>`` é sempre flutuante):

.. image:: ./images/header-menu-fixo.png
   :target: ./images/header-menu-fixo.png
   :alt: header-menu-fixo.png



.. image:: ./images/header-menu-agrupamentos.png
   :target: ./images/header-menu-agrupamentos.png
   :alt: header-menu-agrupamentos.png



.. image:: ./images/header-menu-navegacao.png
   :target: ./images/header-menu-navegacao.png
   :alt: header-menu-navegacao.png


🚀 Instalação
-------------

Via PyPI (Recomendado)
^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   pip install django-dsgovbr

⚙️ Configuração
---------------

1. Adicione ao INSTALLED_APPS
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   # settings.py

   INSTALLED_APPS = [
       # Coloque antes do `django.contrib.admin` para garantir que seja que o template path prevaleça sobre os templates
       # padrões do Django.
       'dsgovbr',
       'django.contrib.admin',
       # ... suas apps
   ]

2. Configure os Context Processors (Opcional)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: python

   # settings.py

   TEMPLATES = [
       {
           'BACKEND': 'django.template.backends.django.DjangoTemplates',
           'DIRS': [],
           'APP_DIRS': True,
           'OPTIONS': {
               'context_processors': [
                   # ... outros context processors
                   'dsgovbr.context_processors.dsgovbr',
               ],
           },
       },
   ]

3. Colete os Arquivos Estáticos
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   python manage.py collectstatic

📖 Uso
------

Templates Base
^^^^^^^^^^^^^^

Use os templates base do DSGovBR nos seus templates Django:

.. code-block:: django

   {% extends "admin/base.html" %}
   {% load static %}

   {% block title %}Minha Página Gov.BR{% endblock %}

   {% block content %}
   <div class="container-fluid">
       <h1>Bem-vindo ao Sistema</h1>

       <!-- Botão primário -->
       <button class="btn btn-primary" type="button">
           Ação Principal
       </button>

       <!-- Mensagem de sucesso -->
       <div class="alert alert-success" role="alert">
           <i class="fas fa-check-circle" aria-hidden="true"></i>
           Operação realizada com sucesso!
       </div>

       <!-- Card -->
       <div class="card">
           <div class="card-header">
               <h2 class="h5 m-0">Título do Card</h2>
           </div>
           <div class="card-body">
               <p>Conteúdo do card seguindo o padrão Gov.BR</p>
           </div>
       </div>
   </div>
   {% endblock %}

Formulários Django
^^^^^^^^^^^^^^^^^^

Os widgets do admin que dependem do ``admin/css/base.css`` do Django (não
carregado pelo tema) funcionam com as variáveis dele definidas no
``dsgovbr.scss`` a partir das ``--bs-*``. Os ``autocomplete_fields`` usam o
Select2 com o tema ``dsgovbr``: largura total, aparência de ``.form-select``
(simples) ou ``.form-control`` (múltiplo, com as opções em badges). Para
manter o tema ``admin-autocomplete`` do Django num campo, use
``data-dsgovbr-ignore``.

Nos relacionamentos (FK), os links de alterar, adicionar, remover e ver usam
ícones do Font Awesome. Nos campos com Select2 eles aparecem no rodapé do
dropdown; os originais ficam ocultos, mas alcançáveis com Tab. Para que todo FK
de select simples dos admins que herdam do ``DSGovBrModelAdmin`` (inclusive os
inlines) vire Select2 local, sobre as opções já carregadas:

.. code-block:: python

   DSGOVBR_FORMS = {"select2_todos_fk": True}  # padrão: False

Ficam de fora os campos múltiplos, ``raw_id_fields``, ``radio_fields`` e os
marcados com ``data-dsgovbr-ignore``. Em FK com muitos registros, prefira
``autocomplete_fields``, que busca no servidor.

Os campos dos formulários renderizados nas páginas do tema recebem as classes do
Bootstrap (``.form-control``, ``.form-select``, ``.form-check-input``) pelo
``dsgovbr/js/dsgovbr_forms.js``, com qualquer ``FORM_RENDERER``. Para declarar
a classe no próprio widget:

.. code-block:: python

   # forms.py
   from django import forms

   class MeuFormulario(forms.Form):
       nome = forms.CharField(
           label="Nome Completo",
           max_length=100,
           widget=forms.TextInput(attrs={
               'class': 'form-control',
               'placeholder': 'Digite seu nome'
           })
       )

       email = forms.EmailField(
           label="E-mail",
           widget=forms.EmailInput(attrs={
               'class': 'form-control',
               'placeholder': 'seuemail@exemplo.gov.br'
           })
       )

       mensagem = forms.CharField(
           label="Mensagem",
           widget=forms.Textarea(attrs={
               'class': 'form-control',
               'rows': 5
           })
       )

Admin do Django
^^^^^^^^^^^^^^^

O pacote fornece templates customizados para o Django Admin com visual Gov.BR:

.. code-block:: python

   # admin.py
   from django.contrib import admin
   from .models import MeuModelo

   @admin.register(MeuModelo)
   class MeuModeloAdmin(admin.ModelAdmin):
       list_display = ['nome', 'status', 'data_criacao']
       list_filter = ['status']
       search_fields = ['nome']

🎨 Componentes Disponíveis
--------------------------

Classes CSS Principais
^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: html

   <!-- Botões -->
   <button class="btn btn-primary">Primário</button>
   <button class="btn btn-outline-primary">Secundário</button>
   <button class="btn btn-link">Terciário</button>

   <!-- Mensagens -->
   <div class="alert alert-info">Informação</div>
   <div class="alert alert-success">Sucesso</div>
   <div class="alert alert-warning">Aviso</div>
   <div class="alert alert-danger">Erro</div>

   <!-- Cards -->
   <div class="card">
       <div class="card-header">Cabeçalho</div>
       <div class="card-body">Conteúdo</div>
       <div class="card-footer">Rodapé</div>
   </div>

   <!-- Campos -->
   <input type="text" class="form-control" placeholder="Digite aqui...">
   <textarea class="form-control"></textarea>
   <select class="form-select">
       <option>Opção 1</option>
   </select>

🔧 Desenvolvimento
------------------

Requisitos
^^^^^^^^^^


* Python 3.10+
* Django 5.2+

Setup para Desenvolvimento
^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   # Clone o repositório
   git clone https://github.com/kelsoncm/django-dsgovbr.git
   cd django-dsgovbr

   # Crie um ambiente virtual
   python -m venv venv
   source venv/bin/activate  # Linux/Mac
   # ou
   venv\Scripts\activate  # Windows

   # Instale as dependências de desenvolvimento
   pip install -e ".[dev]"

   # Execute os testes
   python -m pytest

📝 Licença
----------

Este projeto está licenciado sob a `Licença MIT <https://opensource.org/licenses/MIT>`_.

👥 Contribuindo
---------------

Contribuições são bem-vindas! Por favor:


#. Faça um Fork do projeto
#. Crie uma branch para sua feature (\ ``git checkout -b feature/MinhaFeature``\ )
#. Commit suas mudanças (\ ``git commit -m 'Adiciona MinhaFeature'``\ )
#. Push para a branch (\ ``git push origin feature/MinhaFeature``\ )
#. Abra um Pull Request

📧 Contato
----------

Kelson da Costa Medeiros


* Email: kelsoncm@gmail.com
* GitHub: `@kelsoncm <https://github.com/kelsoncm>`_

🔗 Links Úteis
--------------


* `Design System Gov.BR - Site Oficial <https://www.gov.br/ds/home>`_
* `DS Gov.BR - Componentes <https://www.gov.br/ds/componentes/overview>`_
* `DS Gov.BR - GitHub <https://github.com/govbr-ds>`_
* `Documentação Django <https://docs.djangoproject.com/>`_
* `Acessibilidade Gov.BR <https://www.gov.br/governodigital/pt-br/acessibilidade-digital>`_

📊 Status do Projeto
--------------------


* ✅ Integração básica com Django Admin
* ✅ Templates base Gov.BR
* ✅ Componentes CSS principais
* ✅ Suporte a formulários Django
* 🔄 Em desenvolvimento: Widgets customizados
* 📋 Planejado: Componentes JavaScript interativos

🚀 Próximos Passos
^^^^^^^^^^^^^^^^^^

Planejamos adicionar nas próximas versões:


* Widgets customizados para formulários
* Componentes JavaScript interativos
* Mais templates de exemplo
* Suporte a temas customizados
* Documentação expandida

🙏 Agradecimentos
^^^^^^^^^^^^^^^^^

Agradecemos à equipe do Design System Gov.BR por criar e manter o design system oficial do governo federal brasileiro.

📧 Feedback
^^^^^^^^^^^

Encontrou algum problema ou tem sugestões?
Abra uma `issue <https://github.com/kelsoncm/django-admintheme-dsgovbr/issues>`_ ou contribua com um pull request!

----

..

   Desenvolvido com ❤️ para o ecossistema Gov.BR

.. toctree::
   :hidden:
   :caption: Guia

   start-guide
   publishing
   contribute

.. toctree::
   :hidden:
   :caption: Referência da API

   api/modules
