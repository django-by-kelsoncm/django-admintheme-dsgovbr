// Aplica as classes de formulário do Bootstrap (.form-control, .form-select,
// .form-check-input, .form-range) aos campos renderizados pelo Django, que
// não as recebem por padrão. Funciona com qualquer FORM_RENDERER e também nas
// linhas de inline adicionadas depois (evento "formset:added" do admin).
// Para ignorar um campo ou um bloco: atributo data-dsgovbr-ignore.
(function () {
  'use strict';

  var SEM_CLASSE = ['hidden', 'submit', 'button', 'reset', 'image'];
  var JA_ESTILIZADO = ['form-control', 'form-select', 'form-check-input', 'form-range', 'btn'];

  function classeDo(campo) {
    var tag = campo.tagName.toLowerCase();
    if (tag === 'select') return ['form-select'];
    if (tag === 'textarea') return ['form-control'];
    var tipo = (campo.getAttribute('type') || 'text').toLowerCase();
    if (SEM_CLASSE.indexOf(tipo) !== -1) return [];
    if (tipo === 'checkbox' || tipo === 'radio') return ['form-check-input'];
    if (tipo === 'range') return ['form-range'];
    if (tipo === 'color') return ['form-control', 'form-control-color'];
    return ['form-control'];
  }

  function aplicar(raiz) {
    var campos = (raiz || document).querySelectorAll('input, select, textarea');
    Array.prototype.forEach.call(campos, function (campo) {
      if (campo.closest('[data-dsgovbr-ignore]')) return;
      // Campos internos do Select2: estilizados pelo tema "dsgovbr" (abaixo).
      if (campo.closest('.select2-container')) return;
      for (var i = 0; i < JA_ESTILIZADO.length; i++) {
        if (campo.classList.contains(JA_ESTILIZADO[i])) return;
      }
      classeDo(campo).forEach(function (classe) { campo.classList.add(classe); });
    });
  }

  window.dsgovbrBootstrapFields = aplicar;

  // Select2 do admin (autocomplete_fields): troca o tema "admin-autocomplete",
  // cujo CSS usa as variáveis do base.css do admin (não carregado pelo tema),
  // pelo tema "dsgovbr" (dsgovbr.scss) e põe na caixa a classe do Bootstrap
  // (.form-select ou .form-control). Precisa rodar antes de o autocomplete.js
  // do Django iniciar o Select2, no ready do jQuery: este script fica no fim
  // do <body>. Inclui o formulário vazio (__prefix__) que os inlines clonam.
  function prepararAutocomplete(raiz) {
    var campos = (raiz || document).querySelectorAll('select.admin-autocomplete');
    Array.prototype.forEach.call(campos, function (campo) {
      if (campo.closest('[data-dsgovbr-ignore]')) return;
      if (campo.classList.contains('select2-hidden-accessible')) return;
      campo.setAttribute('data-theme', 'dsgovbr');
      campo.setAttribute('data-container-css-class', campo.multiple ? 'form-control' : 'form-select');
      ocultarLinks(campo);
    });
  }

  // Ações do campo de relacionamento (issue #61): os links de alterar,
  // adicionar, remover e ver do related_widget_wrapper.html aparecem no rodapé
  // do dropdown do Select2. Os links originais ficam no lugar, só ocultos
  // (visually-hidden-focusable): o RelatedObjectLookups.js do Django os acha
  // por nextAll() a partir do select, atualiza o href ao trocar a seleção e
  // abre os popups no clique; pelo teclado continuam alcançáveis com Tab, pois
  // o Select2 fecha o dropdown ao sair da busca. Os botões do dropdown só
  // repassam o clique para eles.
  var ACOES = ['change-related', 'add-related', 'delete-related', 'view-related'];

  function linksDoCampo(campo) {
    var caixa = campo.parentElement;
    if (!caixa || !caixa.classList.contains('related-widget-wrapper')) return [];
    return Array.prototype.filter.call(caixa.children, function (filho) {
      return filho.classList.contains('related-widget-wrapper-link');
    });
  }

  function ocultarLinks(campo) {
    linksDoCampo(campo).forEach(function (link) {
      link.classList.add('visually-hidden-focusable');
    });
  }

  function botaoDaAcao(campo, link) {
    var botao = document.createElement('button');
    botao.type = 'button';
    botao.className = 'btn btn-link btn-sm';
    ACOES.forEach(function (acao) {
      if (link.classList.contains(acao)) botao.classList.add('dsgovbr-select2-acao--' + acao);
    });
    botao.title = link.title;
    botao.setAttribute('aria-label', link.title);
    var icone = link.querySelector('i');
    if (icone) botao.appendChild(icone.cloneNode(true));
    var rotulo = link.querySelector('.visually-hidden');
    if (rotulo) {
      var texto = document.createElement('span');
      texto.textContent = rotulo.textContent;
      botao.appendChild(texto);
    }
    botao.addEventListener('click', function () {
      window.django.jQuery(campo).select2('close');
      link.click();
    });
    botao.dsgovbrLink = link;
    return botao;
  }

  function acoesNoDropdown(campo) {
    var instancia = window.django.jQuery(campo).data('select2');
    var links = linksDoCampo(campo);
    if (!instancia || !instancia.$dropdown || !links.length) return;
    var dropdown = instancia.$dropdown[0];
    if (!dropdown.classList.contains('select2-dropdown')) {
      dropdown = dropdown.querySelector('.select2-dropdown');
    }
    if (!dropdown) return;
    var barra = dropdown.querySelector('.dsgovbr-select2-acoes');
    var nova = !barra;
    if (nova) {
      barra = document.createElement('div');
      barra.className = 'dsgovbr-select2-acoes';
      barra.setAttribute('role', 'toolbar');
      // Sem isto o Select2 trata o mousedown como clique fora, fecha e tira o
      // dropdown do DOM antes do clique no botão.
      barra.addEventListener('mousedown', function (evento) {
        evento.preventDefault();
        evento.stopPropagation();
      });
      links.forEach(function (link) { barra.appendChild(botaoDaAcao(campo, link)); });
      dropdown.appendChild(barra);
    }
    // Sem href: nada selecionado para alterar, ver ou remover.
    Array.prototype.forEach.call(barra.children, function (botao) {
      botao.disabled = !botao.dsgovbrLink.hasAttribute('href');
    });
    // A barra muda a altura do dropdown já posicionado (aberto para cima).
    if (nova && instancia.dropdown && typeof instancia.dropdown._positionDropdown === 'function') {
      instancia.dropdown._positionDropdown();
    }
  }

  window.dsgovbrPrepararAutocomplete = prepararAutocomplete;
  prepararAutocomplete(document);

  // Select2 em todo FK (DSGOVBR_FORMS["select2_todos_fk"], issue #61): o
  // select simples dos campos de relacionamento vira Select2 local, sobre as
  // <option> já renderizadas. O base.html marca o <body> com o idioma do
  // Select2 e o DSGovBrModelAdmin carrega o Select2; sem ele (outro
  // ModelAdmin) os campos ficam como estão. Fora: múltiplos, raw_id_fields,
  // radio_fields e os autocomplete_fields (já são Select2).
  function select2EmTodoFk(raiz) {
    var $ = window.django && window.django.jQuery;
    var idioma = document.body.getAttribute('data-dsgovbr-select2-todos-fk');
    if (idioma === null || !$ || !$.fn.select2) return;
    var campos = (raiz || document).querySelectorAll(
      '.related-widget-wrapper > select:not([multiple]):not(.admin-autocomplete)'
    );
    Array.prototype.forEach.call(campos, function (campo) {
      if (campo.closest('[data-dsgovbr-ignore]')) return;
      if (campo.classList.contains('select2-hidden-accessible')) return;
      // Formulário vazio que os inlines clonam: iniciado no "formset:added".
      if (campo.name.indexOf('__prefix__') !== -1) return;
      var vazia = campo.querySelector('option[value=""]');
      var opcoes = {
        theme: 'dsgovbr',
        containerCssClass: 'form-select',
        width: '100%',
        allowClear: !!vazia && !campo.required
      };
      if (vazia) opcoes.placeholder = { id: '', text: vazia.textContent };
      if (idioma) opcoes.language = idioma;
      ocultarLinks(campo);
      $(campo).select2(opcoes);
    });
  }

  window.dsgovbrSelect2EmTodoFk = select2EmTodoFk;

  if (window.django && window.django.jQuery) {
    var $ = window.django.jQuery;
    $(function () { select2EmTodoFk(document); });
    // Busca do dropdown do Select2 (criada ao abrir, fora do formulário) e
    // ações do campo de relacionamento no rodapé.
    $(document).on('select2:open', function (evento) {
      document.querySelectorAll('.select2-container--dsgovbr .select2-search--dropdown .select2-search__field')
        .forEach(function (busca) { busca.classList.add('form-control'); });
      acoesNoDropdown(evento.target);
    });
  }

  // Elementos criados depois do DOMContentLoaded pelos JS do admin: links do
  // inlines.js ($(document).ready) e a caixa de seleção do SelectFilter2.js
  // (filter_horizontal), criada no "load" antes deste handler.
  function botoesDoAdmin() {
    aplicar(document);
    document.querySelectorAll('.selector button').forEach(function (botao) {
      botao.classList.add('btn', 'btn-outline-primary', 'btn-sm');
    });
    document.querySelectorAll('.add-row a').forEach(function (link) {
      link.classList.add('btn', 'btn-outline-primary', 'btn-sm');
    });
    document.querySelectorAll('a.inline-deletelink').forEach(function (link) {
      link.classList.add('btn', 'btn-link', 'btn-sm');
    });
  }

  // Calendário e relógio (DateTimeShortcuts.js do Django): o Django abre a
  // caixa à direita do ícone e sobe 75px (calendário) ou 30px (relógio),
  // pensando no ícone ao lado do campo. No tema o ícone fica abaixo do campo
  // e a caixa cobria o campo. Aqui ela abre logo abaixo do link, sem passar
  // da borda direita da janela; o espaço vem do margin-top do dsgovbr.scss.
  function posicionarAbaixo(caixa, link) {
    if (!caixa || !link) return;
    var ancora = link.getBoundingClientRect();
    var largura = caixa.offsetWidth;
    var maxEsquerda = document.documentElement.clientWidth - largura;
    var esquerda = Math.max(0, Math.min(ancora.left, maxEsquerda));
    caixa.style.left = esquerda + window.scrollX + 'px';
    caixa.style.top = ancora.bottom + window.scrollY + 'px';
  }

  function calendarioAbaixoDoCampo() {
    var atalhos = window.DateTimeShortcuts;
    if (!atalhos || atalhos.dsgovbrPosicionado) return;
    atalhos.dsgovbrPosicionado = true;
    var abrirCalendario = atalhos.openCalendar;
    var abrirRelogio = atalhos.openClock;
    atalhos.openCalendar = function (num) {
      abrirCalendario.apply(this, arguments);
      posicionarAbaixo(
        document.getElementById(atalhos.calendarDivName1 + num),
        document.getElementById(atalhos.calendarLinkName + num)
      );
    };
    atalhos.openClock = function (num) {
      abrirRelogio.apply(this, arguments);
      posicionarAbaixo(
        document.getElementById(atalhos.clockDivName + num),
        document.getElementById(atalhos.clockLinkName + num)
      );
    };
  }

  window.addEventListener('load', calendarioAbaixoDoCampo);

  window.addEventListener('load', botoesDoAdmin);
  // O jQuery 3 executa o ready de forma assíncrona: registrar aqui, depois do
  // inlines.js, garante rodar após ele criar o "Adicionar outro".
  if (window.django && window.django.jQuery) {
    window.django.jQuery(botoesDoAdmin);
  }

  document.addEventListener('formset:added', function (evento) {
    aplicar(evento.target);
    botoesDoAdmin();
    select2EmTodoFk(evento.target);
  });

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function () { aplicar(document); });
  } else {
    aplicar(document);
  }
})();
