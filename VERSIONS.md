# Histórico de Versões

## 7.0.0

### Bootstrap 5 com o dsgovbr-bootstraped (quebra de compatibilidade)

- **Aparência**: os templates trocam as classes `br-*` do GOV.BR DS por classes do Bootstrap 5.3 com o tema
  [dsgovbr-bootstraped](https://github.com/abrasileirado/dsgovbr-bootstraped) v0.10.0. O CSS do tema e o
  `bootstrap.bundle.min.js` 5.3.8 vêm em `static/vendors/`; o `core-init.js` do GOV.BR DS e o flatpickr não são mais
  carregados, e o SCSS do tema não importa mais o `vendors/serpro`.
- **Quem estende os templates**: markup próprio com `br-*` (botões, mensagens, cards, campos) deixa de ter estilo. Use as
  classes do Bootstrap (`btn btn-primary`, `alert`, `card`, `form-control`…). Utilitários do Bootstrap 4 usados pelo
  GOV.BR DS (`mr-*`, `ml-*`, `text-right`, `sr-only`) viram os do Bootstrap 5 (`me-*`, `ms-*`, `text-end`,
  `visually-hidden`).
- **Header, menu e rodapé**: header com a navbar; menu num offcanvas com list group e pastas por Collapse
  (`menu.localizacao`: `fixo` deixa o menu aberto a partir de 1200px, `flutuante` só pelo botão); novo bloco `menu` no
  `dsgovbr/base.html`; rodapé com `data-bs-theme="dark"`; skiplink com `.visually-hidden-focusable`.
- **Lista do admin**: busca e filtros em Collapse, ações em dropdown, tabela `.table`, paginação `.pagination` e
  densidade da tabela em `dsgovbr_admin_density.js` (substitui o `dsgovbr_admin_submit_line.js`, removido).
- **Formulários**: fieldset em grade, erros com `.invalid-feedback` e o novo `dsgovbr/js/dsgovbr_forms.js`, que aplica
  `.form-control`, `.form-select` e `.form-check-input` aos campos do Django (também nos inlines e no
  `filter_horizontal`).
- **Login e `registration/`**: cards, alertas e campos do Bootstrap; o `dsgovbr_login.scss` foi removido.
- **Cookiebar**: o bloco `cookie_consent` vem vazio (antes era um `div.br-cookiebar` oculto e sem conteúdo).

### Correções no admin

- **Lista do admin**: a tag `dsgovbr_result_list` usava o `change_list_results.html` do Django em vez do
  `change_list_dsgovbr_results.html` do tema.
- **Mídia da lista**: os JS do `ModelAdmin` eram incluídos duas vezes no `change_list.html`.
- **Formulário**: o `submit_buttons_top` imprimia o `{{ request }}` na página.
- **Paginação**: `page_item` monta o HTML com `format_html` (antes, `mark_safe` com f-string), sem `tabindex` por página
  e com `aria-current` na página atual.

## 6.0.1

### Compatibilidade com Django 6.1

- **`dsgovbr_result_list`**: passa o nome da tag ao `InclusionAdminNode`, exigido a partir do Django 6.1 (a lista do
  admin quebrava com `missing 1 required positional argument: 'token'`).

### Correções

- **Menu do admin**: `get_full_admin_app_list` usava `admin.site.get_app_list`, que no `DSGovBrAdminSite` chama o
  próprio menu (recursão infinita e menu vazio). Agora usa a implementação base do `AdminSite`.
- **Sair**: o item "Sair" usa a rota `logout` ou, na falta dela, `admin:logout`, em vez de quebrar.
- **Logs**: `print` de depuração removidos; erros vão para o `logging`.
- **Links fixos**: o rodapé do menu não mostra mais "Link externo 1/2"; os links vêm de
  `DSGOVBR_HEADER["menu"]["footer"]["links"]`. A versão no rodapé só tem link com `PROJECT_RELEASES_URL` (antes
  apontava para o repositório `cte-zl-ifrn/integration-integrador_ava`).

### Dependências

- **Declaradas**: `django-compressor` e `django-libsass`, usados pelos templates (`{% compress %}` com SCSS).
- **Extra `import-export`**: `django-import-export`, para o `DSGovBrModelAdmin`.
- **Documentação**: configuração do compressor, `COMPRESS_OFFLINE` e `DSGovBrAdminConfig` no README.

### Correções de segurança

- **Dependências de desenvolvimento**: atualização do `uv.lock` para versões corrigidas de Django (6.0.8), Pillow
  (13.0.0), black, certifi, filelock, sqlparse, tablib, urllib3 e virtualenv, resolvendo os alertas do Dependabot.

## 6.0.0

### Compatibilidade com Django 6.0.x

- **Django 6.0**: Atualização da compatibilidade do pacote para suportar Django 6.0.x.
- **Python >= 3.12**: Elevação da versão mínima suportada do Python para 3.12 (conforme exigido pelo Django 6.0).
- **CI/CD**: Atualização das matrizes de teste do GitLab CI e GitHub Actions para testar contra o Django 6.0.x e
  Python 3.12+.
- **Remoção de Legado**: Descontinuado o suporte oficial para Django 5.2 e versões inferiores, bem como Python 3.10 e 3.11.

## 5.2.4

### Refatoração e Expansão dos Templates Administrativos

- **Formulários Django**: Refatoração completa dos templates de formulários, com criação de arquivos dedicados para
  widgets e atributos, como `attrs.html`, `input.html`, `multiwidget.html` e diversos outros para tipos de campos
  (checkbox, radio, select, etc.).
  - Melhoria na estrutura, clareza e manutenibilidade dos formulários.
  - Facilita futuras customizações e ampliações.
- **Histórico de Objetos**: Refatoração dos templates de histórico (`object_history.html`, `object_history_form.html`,
  `object_history_list.html`, `submit_line.html`) para melhor apresentação, organização e lógica de exibição.
- **Templates de Listagem**: Criação e reorganização de templates para resultados de listagem, cabeçalho, rodapé e
  paginação, incluindo:
  - `change_list_dsgovbr_results.html`, `change_list_footer.html`, `change_list_header.html`, `pagination.html`.
  - Remoção do template antigo `change_list_results.html`.
- **Aprimoramento dos Templates de Ações e Filtros**:
  - Refatoração dos templates `actions.html`, `filter.html`, `filters.html` e inclusão de novos filtros dinâmicos e
  dropdowns para melhor usabilidade.
  - Implementação de lógica de filtros dinâmicos na interface administrativa, permitindo aplicar/remover filtros de
  forma interativa.
- **Aprimoramento dos Templates de Ferramentas de Objeto**:
  - Novos templates e lógica para exibição de ferramentas de objeto e ações de instância na interface administrativa.
  - Melhoria na apresentação e usabilidade dos botões de ação.
- **Aprimoramento dos Templates de Exportação/Importação**:
  - Ajustes visuais e funcionais nos templates de exportação/importação, incluindo melhorias no checkbox "Selecionar
  todos" e botões de envio.
- **Aprimoramento dos Templates de Login e Histórico**:
  - Melhorias de layout e experiência do usuário nos templates de login e histórico de objetos.

### Novos Arquivos e Estrutura

- **Novos templates criados**: Diversos arquivos adicionados para granularidade e reutilização, especialmente em
  `src/dsgovbr/templates/django/forms/widgets/` e `src/dsgovbr/templates/admin/`.
- **Novos arquivos JavaScript**: Adição de `dsgovbr_admin_actions.js`, `dsgovbr_admin_filters.js`,
  `dsgovbr_admin_submit_line.js` para manipulação dinâmica de ações, filtros e botões na interface administrativa.

### Melhorias de Usabilidade e Acessibilidade

- **Dropdowns e Botões**: Inclusão de dropdowns para ações de submissão e filtros, tornando a navegação mais intuitiva.
- **Aprimoramento Visual**: Ajustes de CSS em `dsgovbr.css` para tabelas, botões, feedbacks e alinhamento de elementos.
- **Acessibilidade**: Melhoria na navegação por teclado e uso de elementos semânticos nos templates.

### Refatoração e Organização do Código

- **Admin Python**: Criação e refatoração de `src/dsgovbr/admin.py` para centralizar lógica de ações, ferramentas de
  objeto e filtros dinâmicos.
- **Template Tags**: Expansão de `templatetags/dsgovbr_admin_list.py` e `templatetags/dsgovbr.py` para suportar novas
  funcionalidades e simplificar geração de listas/resultados.
- **Remoção de Código Morto**: Exclusão de código obsoleto e simplificação de imports.

### Estatísticas da versão 5.2.4

- **56 arquivos alterados**
- **551 inserções(+), 322 deleções(-)**
- **Criação de mais de 40 novos arquivos de template e JS**

### Observações

- Esta versão representa uma grande evolução na estrutura dos templates administrativos, tornando o projeto mais
  modular, flexível e alinhado ao Design System GovBR.
- Recomenda-se revisar customizações locais de templates administrativos ao atualizar para esta versão.

## 5.2.3

### Melhorias na Interface Administrativa

- **Interface do Admin**: Refatoração completa dos templates do Django Admin com Design System GovBR
  - Reorganização do template base (`base.html`) com melhorias estruturais
  - Melhorias na listagem de aplicações (`app_list.html`) com melhor organização visual
  - Aprimoramento do formulário de alteração (`change_form.html`) com layout mais intuitivo
  - Otimização da linha de submissão (`submit_line.html`) com botões mais visíveis
  - Ajustes no fieldset (`includes/fieldset.html`) para melhor apresentação de campos
  - Isolamento de cada aplicação em seu próprio menu-folder para melhor navegação
  - Adição de home ao menu principal
  - Correção: rodapé agora é exibido corretamente no final da tela
  - Correção: campos só são apresentados como erro quando realmente possuem erro

### Novos Recursos

- **Favicons**: Implementação completa do sistema de favicons do GovBR
  - Adição de favicon padrão do GovBR (favicon.ico atualizado)
  - Inclusão de apple-touch-icon.png
  - Adição de favicons em múltiplos tamanhos (16x16, 32x32)
  - Inclusão de mstile-144x144.png para Windows
  - Adição de safari-pinned-tab.svg
  - Criação de site.webmanifest para PWA
  - Template dedicado para favicons (`dsgovbr/favicon.html`)

- **Assets GovBR**: Novos recursos visuais
  - Adição de logo GovBR em PNG e SVG (`vendors/serpro/govbr.png` e `govbr.svg`)

- **Estilos CSS**: Novo arquivo `dsgovbr.css` com estilos customizados
  - Ajustes de altura mínima do container
  - Estilos para mensagens de erro e feedback
  - Formatação de botões secundários pequenos
  - Estilização de fieldsets com br-card
  - Melhorias tipográficas em legendas e descrições

- **Template Tags**: Criação de template tags customizadas (`templatetags/dsgovbr.py`)
  - Novas tags para facilitar o uso do Design System

- **Context Processors**: Melhorias nos processadores de contexto
  - Leitura e disponibilização das settings para o tema
  - Melhor integração com configurações do Django

### Melhorias de Integração

- **Import/Export**: Ajustes no template de importação (`import_export/import.html`)
- **Simple History**: Otimização do template de histórico de objetos
- **Versionamento**: Numeração de versão agora indica a versão do Django suportada

### Atualizações de Dependências (GitHub Actions)

- Atualização do actions/checkout de v4 para v6
- Atualização do actions/setup-python de v5 para v6
- Atualização do actions/download-artifact de v4 para v7
- Atualização do actions/upload-artifact de v4 para v6
- Ajustes nos workflows de publicação no PyPI e testes

### Estatísticas da versão 5.2.3

- **26 arquivos alterados**: 298 inserções(+), 227 deleções(-)
- **9 novos arquivos** adicionados (incluindo favicons, logos e templates)
- **Refatoração significativa** nos templates do Django Admin para melhor usabilidade
