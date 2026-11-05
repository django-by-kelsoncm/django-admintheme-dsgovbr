
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

Os templates compilam o SCSS do DS Gov.BR com o ``django-compressor``:

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
   <div class="br-container">
       <h1>Bem-vindo ao Sistema</h1>

       <!-- Botão Primário -->
       <button class="br-button primary" type="button">
           Ação Principal
       </button>

       <!-- Mensagem de Sucesso -->
       <div class="br-message success">
           <div class="icon">
               <i class="fas fa-check-circle"></i>
           </div>
           <div class="content">
               Operação realizada com sucesso!
           </div>
       </div>

       <!-- Card -->
       <div class="br-card">
           <div class="card-header">
               <h3>Título do Card</h3>
           </div>
           <div class="card-content">
               <p>Conteúdo do card seguindo o padrão Gov.BR</p>
           </div>
       </div>
   </div>
   {% endblock %}

Formulários Django
^^^^^^^^^^^^^^^^^^

Os formulários Django automaticamente usam os estilos do DS Gov.BR:

.. code-block:: python

   # forms.py
   from django import forms

   class MeuFormulario(forms.Form):
       nome = forms.CharField(
           label="Nome Completo",
           max_length=100,
           widget=forms.TextInput(attrs={
               'class': 'br-input',
               'placeholder': 'Digite seu nome'
           })
       )

       email = forms.EmailField(
           label="E-mail",
           widget=forms.EmailInput(attrs={
               'class': 'br-input',
               'placeholder': 'seuemail@exemplo.gov.br'
           })
       )

       mensagem = forms.CharField(
           label="Mensagem",
           widget=forms.Textarea(attrs={
               'class': 'br-textarea',
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
   <button class="br-button primary">Primário</button>
   <button class="br-button secondary">Secundário</button>
   <button class="br-button tertiary">Terciário</button>

   <!-- Mensagens -->
   <div class="br-message info">Informação</div>
   <div class="br-message success">Sucesso</div>
   <div class="br-message warning">Aviso</div>
   <div class="br-message error">Erro</div>

   <!-- Cards -->
   <div class="br-card">
       <div class="card-header">Cabeçalho</div>
       <div class="card-content">Conteúdo</div>
       <div class="card-footer">Rodapé</div>
   </div>

   <!-- Inputs -->
   <input type="text" class="br-input" placeholder="Digite aqui...">
   <textarea class="br-textarea"></textarea>
   <select class="br-select">
       <option>Opção 1</option>
   </select>
