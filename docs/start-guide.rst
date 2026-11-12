
Guia de início rápido
=====================

🚀 Instalação**
---------------

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
                   'dsgovbr.context_processors.layout_settings',
               ],
           },
       },
   ]

3. Configure o compressor (SCSS)
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

A aparência vem do `dsgovbr-bootstrapped <https://github.com/abrasileirado/dsgovbr-bootstrapped>`_
(Bootstrap 5 com a cara do GOV.BR DS), já incluído no pacote. Os templates
compilam só o SCSS próprio do tema com o ``django-compressor``:

.. code-block:: python

   # settings.py

   INSTALLED_APPS += ['compressor']
   STATICFILES_FINDERS = [
       'django.contrib.staticfiles.finders.FileSystemFinder',
       'django.contrib.staticfiles.finders.AppDirectoriesFinder',
       'compressor.finders.CompressorFinder',
   ]
   COMPRESS_PRECOMPILERS = (('text/x-scss', 'django_libsass.SassCompiler'),)

4. Colete os Arquivos Estáticos
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

.. code-block:: bash

   python manage.py collectstatic
   # em produção, com COMPRESS_OFFLINE = True
   python manage.py compress

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
