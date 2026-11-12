# Histórico de Versões

## 8.0.0

### Web components do dsgovbr-bootstraped 0.18.0 (issue #51)

- **Vendor**: `dsgovbr-bootstraped` passa para a 0.18.0, com `dsgovbr-bootstraped-componentes.js` e
  `dsgovbr-bootstraped-cookies.js`.
- **Header, breadcrumb, título e ações**: o `dsgovbr/base.html` usa o `<dsgovbr-header>`, que fica fixo no topo com o
  breadcrumb (`<dsgovbr-breadcrumb>`), o título da página e as ações (bloco `title_actions`). Blocos novos:
  `page_title` e `header_home_url`. Os blocos `content_title` e `content_subtitle` saíram (o título vai para o header
  por `page_title`; em popup, `<h1>` direto). `breadcrumb`, `breadcrumb_home_url` e `title_actions` continuam, mas o
  `breadcrumb` passa a receber `<dsgovbr-item>` no lugar de `<li class="breadcrumb-item">`.
- **Menu**: `<dsgovbr-menu>` com `<dsgovbr-pasta>` por app. Subitens são achatados ("Pai › Filho"), o badge vira texto
  e a cor do ícone não é aplicada.
- **Rodapé**: `<dsgovbr-footer>` (sempre no modo escuro).
- **Cookiebar**: `<dsgovbr-cookiebar>` pela nova configuração `DSGOVBR_COOKIEBAR` (desligada por padrão); com ela
  ligada o header ganha o botão de configurações.
- **Lista do admin**: `<dsgovbr-tabela>` com busca, filtros (um valor por filtro, inclusive os de data com vários
  parâmetros), densidade, barra de selecionados com as ações em lote por POST e paginação (`<dsgovbr-paginacao>`).
  O formulário da lista passou de GET para POST com CSRF, o que faz as ações em lote funcionarem (antes enviavam GET).
  Tags novas: `dsgovbr_filtros`, `dsgovbr_pagina_href` e `dsgovbr_mostrar_todos_href`.
- **Cola JS**: `dsgovbr/js/dsgovbr_componentes.js` (busca do header, "Sair" por POST, filtros e ações em lote). O que
  falta nos componentes foi aberto como issues na lib (#76 a #81).
- **Removido** (breaking):
  - Templates `dsgovbr/header.html`, `dsgovbr/avatar.html`, `dsgovbr/menu_item_label.html`,
    `dsgovbr/redes_sociais.html`, `admin/nav_sidebar.html`, `admin/change_list_header.html`,
    `admin/change_list_footer.html`, `admin/change_list_tools.html`, `admin/search_form.html`,
    `admin/pagination.html`, `admin/filters.html`, `admin/filter.html`, `admin/actions.html` e
    `admin/change_list_admin_actions.html`.
  - JS `admin/js/dsgovbr_admin_actions.js`, `dsgovbr_admin_filters.js` e `dsgovbr_admin_density.js`, e as tags
    `page_item`, `choices`, `first_query_param` e `dsgovbr_admin_list_filter`.
  - Configurações `DSGOVBR_HEADER`: `links.em_linha`, `funcionalidades.em_linha`, `menu.localizacao`, `menu.padding`,
    `menu.header` e, em `login`, `type`, `default_avatar_url`, `saudacao`, `name_to_show` e `dropdown.show*`. Avatar,
    foto e papel do usuário não são mais exibidos; o link do logo agora é o do título.
  - SCSS: avatar, menu fixo, submenus, barra de selecionados e densidade "Baixa" (os componentes cuidam disso).
  - Sandbox: `header-behavior.js` e `_header-custom.scss`, que usavam o `.br-header` e nenhum template referenciava.
- Importar e Exportar (`DSGovBrModelAdmin`) aparecem como botões na barra da página.

## 7.5.4

### Atualização para o dsgovbr-bootstraped v0.11.2 (issue #49)

- O CSS (`dsgovbr-bootstraped.min.css`) e o JS do seletor de modo (`dsgovbr-bootstraped-modo.js`) vendorizados passam a
  referenciar a release
  [v0.11.2](https://github.com/abrasileirado/dsgovbr-bootstraped/releases/tag/v0.11.2) do dsgovbr-bootstraped.
- Os arquivos da v0.11.2 são idênticos aos que já estavam no pacote (a release só muda os exemplos do painel); nenhum
  asset em `static/vendors/` foi alterado. A documentação deixa de citar a v0.10.0.

## 7.5.3

### Documentação: sem "Editar no GitHub" nas páginas da API (issue #45)

- As páginas de `docs/api/`, geradas pelo `sphinx.ext.apidoc`, deixam de mostrar o botão "Editar no GitHub", que
  levava a 404. Usa a opção `edit_on_github_exclude` do dsgovbr-sphinx-theme 0.1.2.

## 7.5.2

### Documentação com o tema dsgovbr-sphinx-theme (issue #43)

- A documentação Sphinx troca o `sphinx_rtd_theme` pelo
  [dsgovbr-sphinx-theme](https://github.com/abrasileirado/dsgovbr-sphinx-theme) (visual GOV.BR DS, modo escuro e
  diretivas `br-*` para componentes do dsgovbr-bootstraped).
- A referência da API passa a ser gerada pelo `sphinx.ext.apidoc` no próprio build, com o Django configurado no
  `docs/conf.py`; antes o autodoc falhava ao importar os módulos e a referência saía vazia.
- O workflow `docs.yml` compila com `-W` (aviso vira erro) e instala as dependências de `docs/requirements.txt`.
- Índice com `toctree` (guia e API) e correções de reST em `publishing.rst` e `index.rst`.

## 7.5.1

### Menu sem estado entre requisições (issue #38)

- **Segurança**: o `MenuRegistry.get_menu_list` gravava no registry global (`register_folder`) as pastas do admin que o
  usuário atual via. Depois que um superusuário abria o admin, essas pastas voltavam no menu de qualquer usuário, e o
  `app_index` de um app sem permissão passava a responder 200 em vez de 404. O resultado dependia de quem tinha acessado
  antes, inclusive entre workers. Agora as pastas do admin são montadas só para a requisição; o registry guarda apenas o
  que os `menus.py` registram.
- `DSGovBrAdminSite.app_index` dá 404 quando o usuário não vê nenhum model do app (permissões reais), mesmo que um
  `menus.py` registre uma pasta com o mesmo `app_label`.

## 7.5.0

### Seletor de modo claro/escuro (issue #41)

- **Botão no header** (ícone `fas fa-adjust`), ao lado das funcionalidades: alterna entre claro e escuro. Usa o JS
  opcional do [dsgovbr-bootstraped](https://github.com/abrasileirado/dsgovbr-bootstraped) v0.11.0
  (`vendors/dsgovbr-bootstraped/dsgovbr-bootstraped-modo.js`), carregado no `<head>` para aplicar o modo antes da
  primeira pintura.
- Sem escolha salva, segue o modo do sistema (`prefers-color-scheme`); a escolha fica no `localStorage` do navegador.
  **Atenção**: com o seletor ligado (padrão), quem usa o sistema no modo escuro passa a ver o admin escuro.
- Configurável em `DSGOVBR_HEADER["modo"]`: `show` (padrão `True`), `label` e `icon`. Com `"show": False` o botão e o
  script somem e nada muda em relação à 7.4.0.

## 7.4.0

### Modo escuro (issue #37)

- **`data-bs-theme="dark"`**: o dsgovbr-bootstraped só troca as `--bs-*` globais e vários componentes guardavam cores
  fixas do modo claro (texto `#333`, azul `#1351b4`, fundo `#f8f8f8`), ilegíveis no fundo escuro. O `dsgovbr.scss`
  faz esses componentes usarem as variáveis do Bootstrap dentro de `[data-bs-theme="dark"]`; o modo claro não muda.
- **Corrigidos**: título, subtítulo, links e busca do header; item atual do breadcrumb; texto de `.form-control`,
  `.form-select` (também nas opções do `filter_horizontal`) e `.input-group-text`; botões `btn-outline-primary`,
  `btn-outline-secondary` e `btn-outline-dark` (Cancelar, botões do seletor); itens de dropdown, paginação,
  list group, menu lateral (itens, submenus e item atual), abas, accordion, toast, progress e spinner.
- Menu com `data-bs-theme="light"` próprio (ações da barra de seleção da lista) mantém as cores do vendor.
- O tema não traz seletor de modo: o projeto põe `data-bs-theme` no `<html>` (ou num contêiner).

### Calendário e relógio abaixo do link

- O `DateTimeShortcuts.js` do Django abre a caixa à direita do ícone e 75px (calendário) ou 30px (relógio) acima dele,
  pensando no ícone ao lado do campo. No tema o ícone fica abaixo do campo e a caixa cobria o campo. O
  `dsgovbr_forms.js` passa a abrir a caixa logo abaixo do link "Hoje"/"Agora", sem passar da borda direita da janela.

## 7.3.3

### Select2 vazio em linha nova de inline (issue #35)

- **Autocomplete simples vazio**: sem valor e sem placeholder (linha criada por "Adicionar outro" num inline), a caixa
  do Select2 do tema `dsgovbr` encolhia para a altura do padding. Agora tem a altura de uma linha de texto, igual à dos
  outros campos.
- **Sandbox**: inline "Serviços do órgão" (`Servico.orgaos_envolvidos.through`) na página de Órgão, com
  `autocomplete_fields = ("servico",)`, para validar o Select2 em inline.

## 7.3.2

### Widgets do admin sem o base.css do Django (issue #33)

- **Variáveis do admin**: o `dsgovbr.scss` define as variáveis do `admin/css/base.css` (`--border-color`,
  `--body-bg`, `--body-fg`, `--primary`, `--selected-row`, `--hairline-color`…) a partir das `--bs-*`, também no modo
  escuro. O CSS dos widgets do Django e de pacotes de terceiros que as usam volta a ter borda e fundo.
- **Autocomplete (Select2)**: os `autocomplete_fields` apareciam sem borda e com 280px de largura. O
  `dsgovbr_forms.js` troca o tema `admin-autocomplete` pelo `dsgovbr`: largura total, caixa com `.form-select`
  (simples) ou `.form-control` (múltiplo, opções escolhidas em badges), foco, dropdown e opção selecionada no padrão do
  tema. `data-dsgovbr-ignore` mantém o tema do Django.
- **Relacionamentos**: o `admin/widgets/related_widget_wrapper.html` tinha o `.related-widget-wrapper` comentado e sem
  `data-popup`; os links de alterar/remover ficavam sem `href` e o "adicionar" não abria o popup. Voltou o wrapper,
  com o link "ver" e os ícones alinhados ao campo.
- **Calendário e relógio**: os campos de data/hora (o `widgets.css` do Django não é carregado) ganharam ícones, caixa
  com fundo, borda e sombra e o dia/hora em destaque.
- **Sandbox**: `autocomplete_fields` em Notícia (categoria e tags) e em Servidor (órgão).

## 7.3.1

### Segurança

- **Menu com as permissões do usuário**: `menus.get_full_admin_app_list` montava o menu com um usuário fictício
  superusuário, e o `DSGovBrAdminSite.get_app_list`, o `available_apps` e o `admin_app_list` mostravam a todo usuário
  staff os apps e models sem permissão. Agora usam as permissões reais; quem não entra no admin (inativo ou sem
  `is_staff`) não vê os apps do admin no menu. Itens registrados no `menus.py` seguem com `permission`/`check`.

### Configuração

- `PROJECT_HOME_URL` (contexto `project_home_url`): início do site na casa do breadcrumb fora do admin, no "Voltar ao
  Início" do logout e no `password_reset_done`. Sem ele, o prefixo do script (`FORCE_SCRIPT_NAME`/subcaminho), em vez
  do `/` fixo.
- `DSGOVBR_HEADER["login"]["default_avatar_url"]`: foto padrão do avatar `fotografico` para quem não tem foto. A
  chave `dsgovbr.user_avatar` (URL externa da freepik, não usada pelos templates) foi removida.
- Rodapé: `PROJECT_LICENSE_URL` vazio mostra a licença sem link (antes gerava `<a href="">`).
- Página que esvazia o bloco `menu` não mostra mais o botão do menu no header.

## 7.3.0

### Menu: submenus, badges, cor e permissões em lista

- **Submenus em vários níveis**: `register_item(..., parent=...)` com o item pai, o nome dele ou o caminho de nomes
  (`["Utilitários", "Diagnóstico"]`); ou `MenuItem.add_item`. No menu, cada submenu é um Collapse aninhado no list group
  (`dsgovbr/menu_items.html`), já aberto quando a página atual está dentro dele.
- **Badges**: `badge=MenuItemBadge(label, color)` em pastas e itens; `label` pode ser `label(request)` (contador).
  Texto vazio ou `None` esconde o selo.
- **Cor**: `color` (cor do Bootstrap: `danger`, `success`…) aplicada ao ícone.
- **Permissões em lista**: `permission=["app.view_x", "app.change_x"]` basta qualquer uma (`menus.has_permission`).
- **Ícone padrão do item**: `DSGOVBR_DEFAULT_MENU_ICON` (padrão `fas fa-angle-right`); a pasta sem ícone usa
  `DSGOVBR_DEFAULT_APP_ICON`. O padrão é lido na renderização, então `override_settings` vale.
- **Pastas e submenus vazios somem**: sem link e sem itens visíveis para o usuário.
- **Pasta do admin com `permission`/`check`** no `menus.py` agora some para quem não passa na regra (antes só valia
  para pastas fora do admin).
- Sandbox: pasta "Extras" com o submenu "Laboratório > Diagnóstico", badges e cor.

## 7.2.0

### Cards na página inicial e na página do app

- **Página inicial do admin**: uma seção por app com os models em cards do GOV.BR DS (ícone, nome com link, "Ver
  lista"/"Visualizar" e "Adicionar"). Antes só aparecia o texto de boas-vindas.
- **Página do app**: os cards só do app (`admin/includes/model_cards.html`).
- **Permissões**: o `DSGovBrAdminSite.index` e o `app_index` usam `get_cards_app_list`, a lista do Django com as
  permissões do usuário; o menu continua com `get_app_list`.
- **Ícones**: `AppConfig.icon` e `ModelAdmin.icon`, com padrões `fas fa-folder` e `fas fa-table`
  (`DSGOVBR_DEFAULT_APP_ICON`, `DSGOVBR_DEFAULT_MODEL_ICON`), no menu e nos cards (`dsgovbr/icons.py`).

### Correções de ícones e breadcrumb

- O ícone do model nunca chegava ao menu (`getattr` num `dict` em `menus.py`); o padrão do model no menu passa de
  `fas fa-angle-right` para `fas fa-table`.
- Breadcrumb do admin: os templates sobrescreviam o bloco `breadcrumbs` do Django, que o tema não usa, e só aparecia o
  título. Agora o `admin/base.html` monta app > lista > objeto > página atual, e a casa leva ao `admin:index`.

## 7.1.0

### Header, menu e rodapé parametrizáveis

- **Header**: `DSGOVBR_HEADER["links"]["em_linha"]` e `DSGOVBR_HEADER["funcionalidades"]["em_linha"]` (padrão `False`)
  mostram os links e os ícones na linha do header a partir de 1200px; abaixo disso continuam no dropdown.
- **Rodapé do menu**: `DSGOVBR_HEADER["menu"]["footer"]` aceita `logos` (`[{src, alt}]`), `redes_sociais`
  (`[{label, icon, url}]`) e `licenca`, além dos `links` que já existiam.
- **Rodapé da página**: `DSGOVBR_FOOTER` aceita `logo` e `assinatura` (`{src, alt}`), `colunas`
  (`[{titulo, links: [{label, url, target}]}]`), `redes_sociais` e `texto` (antes do copyright).
- Novo template `dsgovbr/redes_sociais.html`. Tudo vem vazio por padrão: sem configuração, nada muda.
- Sandbox configurado com todos os detalhes.

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
- **Layout do exemplo "Painel administrativo" do dsgovbr-bootstraped**: header com a navbar; header, conteúdo e rodapé
  em `container-lg` (padrão de `width_style` passa de `fluid` para `lg`); menu num offcanvas com list group e pastas por
  Collapse (padrão de `menu.localizacao` passa de `fixo` para `flutuante`; `fixo` deixa o menu aberto a partir de
  1200px); título em `h3` com o novo bloco `title_actions` à direita; novo bloco `menu` no `dsgovbr/base.html`; rodapé
  com `data-bs-theme="dark"`; skiplink com `.visually-hidden-focusable`.
- **Lista do admin**: "Adicionar", busca, filtros e mais opções na linha do título (`admin/change_list_tools.html`);
  busca e filtros em Collapse, ações em dropdown, tabela `.table` com cabeçalho sem cor de link, paginação
  `.pagination` e densidade da tabela em `dsgovbr_admin_density.js` (substitui o `dsgovbr_admin_submit_line.js`, removido).
- **Formulários**: fieldset em grade, erros com `.invalid-feedback` e o novo `dsgovbr/js/dsgovbr_forms.js`, que aplica
  `.form-control`, `.form-select` e `.form-check-input` aos campos do Django (também nos inlines e no
  `filter_horizontal`).
- **Login e `registration/`**: cards, alertas e campos do Bootstrap; o `dsgovbr_login.scss` foi removido.
- **Usuário no header**: Sign-in com avatar no formato do `avatar-dropdown` do GOV.BR DS (`dsgovbr/avatar.html`,
  avatar de 32px com fundo `primary`, "Olá, **Nome**" e seta); o avatar grande do menu do usuário usa a mesma regra
  (foto, ícone ou inicial). Padrão de `login.saudacao` passa de `None` para `"Olá, "`.
- **Cookiebar**: o bloco `cookie_consent` vem vazio (antes era um `div.br-cookiebar` oculto e sem conteúdo).

### Correções no admin

- **Lista do admin**: a tag `dsgovbr_result_list` usava o `change_list_results.html` do Django em vez do
  `change_list_dsgovbr_results.html` do tema.
- **Mídia da lista**: os JS do `ModelAdmin` eram incluídos duas vezes no `change_list.html`.
- **Formulário**: o `submit_buttons_top` imprimia o `{{ request }}` na página.
- **Sair**: era um link GET (com `target="_blank"`) e o `LogoutView` do Django 5+ responde 405; agora é um formulário
  POST com CSRF na mesma aba. Itens do menu do usuário aceitam `"method": "post"`.
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
