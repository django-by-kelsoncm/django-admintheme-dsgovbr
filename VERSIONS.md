# Histórico de Versões

## 6.0.1

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
