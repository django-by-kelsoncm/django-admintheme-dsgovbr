// Cola entre o Django e os web components do dsgovbr-bootstraped (0.18.0).
// Cada bloco cobre algo que o componente ainda não faz sozinho e deve sair
// daqui quando a lib trouxer o recurso (issues abertas em
// abrasileirado/dsgovbr-bootstraped):
//   - busca do header com ação, nome e autocomplete   (#76)
//   - item de menu que envia por POST (o "Sair")      (#77)
//   - <dsgovbr-tabela>: envio nativo das ações em lote (#78)
//   - <dsgovbr-filtro>: escolha única                 (#79)
// Carregue com defer, depois do dsgovbr-bootstraped-componentes.js.
(function () {
  'use strict';

  // Executa fn quando o componente já montou (atributo data-dsgovbr-montado).
  function quandoMontado(el, fn) {
    if (el.hasAttribute('data-dsgovbr-montado')) {
      fn(el);
      return;
    }
    var observador = new MutationObserver(function () {
      if (el.hasAttribute('data-dsgovbr-montado')) {
        observador.disconnect();
        fn(el);
      }
    });
    observador.observe(el, { attributes: true, attributeFilter: ['data-dsgovbr-montado'] });
  }

  // ---- header: busca do site (action, name, id e autocomplete) ----------------
  // O <dsgovbr-header busca> gera o formulário sem action, sem name no campo e
  // sem id fixo; os dados vêm de data-busca-acao e data-busca-autocomplete.
  // Só aceita caminho local ("/busca/?x=1"): sem esquema, sem host e sem "//". Um
  // data-* adulterado não leva a busca para outro site nem a um "javascript:".
  var CAMINHO_LOCAL = /^\/(?!\/)[\w\-./%?=&+~:@,;!*()]*$/;

  function configurarBusca(header) {
    var acao = header.getAttribute('data-busca-acao');
    var form = header.querySelector('form[role="search"]');
    var campo = form && form.querySelector('input[type="search"]');
    if (!CAMINHO_LOCAL.test(acao) || !campo) return;

    form.setAttribute('action', acao);
    form.setAttribute('method', 'get');
    campo.name = 'q';
    campo.id = 'searchbox'; // alvo do atalho "Ir para a busca" e do searchbox.js
    campo.setAttribute('autocomplete', 'off');
    var rotulo = form.querySelector('label');
    if (rotulo) rotulo.setAttribute('for', 'searchbox');

    var sugestoes = header.getAttribute('data-busca-autocomplete');
    if (CAMINHO_LOCAL.test(sugestoes)) {
      campo.setAttribute('data-autocomplete-url', sugestoes);
      campo.setAttribute('aria-controls', 'searchbox-autocomplete-results');
      var lista = document.createElement('div');
      lista.id = 'searchbox-autocomplete-results';
      lista.className = 'list-group dsgovbr-autocomplete shadow';
      form.classList.add('position-relative');
      form.appendChild(lista);
    }
  }

  // ---- header: itens do menu do usuário que exigem POST -----------------------
  // O <dsgovbr-item> só gera links GET. Para cada item com método POST o template
  // renderiza um <form data-dsgovbr-link-post action="URL"> com o CSRF; clicar no
  // link do header com o mesmo href envia o formulário.
  document.addEventListener('click', function (evento) {
    var link = evento.target.closest ? evento.target.closest('dsgovbr-header a[href]') : null;
    if (!link) return;
    var href = link.getAttribute('href');
    var forms = document.querySelectorAll('form[data-dsgovbr-link-post]');
    for (var i = 0; i < forms.length; i++) {
      if (forms[i].getAttribute('action') === href) {
        evento.preventDefault();
        forms[i].submit();
        return;
      }
    }
  });

  // ---- lista do admin: <dsgovbr-tabela data-dsgovbr-changelist> ---------------
  function ligarLista(tabela) {
    var form = tabela.closest('form');

    // Escolha única por filtro: o Django usa um valor por filtro.
    tabela.addEventListener('change', function (evento) {
      var marcado = evento.target;
      if (!marcado.matches || !marcado.matches('input[data-tabela-filtro]') || !marcado.checked) return;
      tabela.querySelectorAll('input[data-tabela-filtro]').forEach(function (outro) {
        if (outro !== marcado && outro.name === marcado.name) outro.checked = false;
      });
      if (typeof tabela.atualizarChips === 'function') tabela.atualizarChips();
    });

    // Ação em lote: preenche o "action" do ChangeList e envia o formulário (POST),
    // que já leva os _selected_action marcados.
    tabela.addEventListener('dsgovbr:tabela-acao', function (evento) {
      var campo = form && form.querySelector('input[name="action"]');
      if (!campo || !evento.detail.valores.length) return;
      campo.value = evento.detail.acao;
      form.submit();
    });

    // Busca e filtros: monta a URL do ChangeList (GET), mantendo ordenação e
    // demais parâmetros, tirando os filtros antigos e a página.
    tabela.addEventListener('submit', function (evento) {
      var consulta = evento.target;
      if (!consulta.matches || !consulta.matches('form[data-tabela-consulta]')) return;
      evento.preventDefault();

      var url = new URL(window.location.href);
      var params = url.searchParams;
      (tabela.getAttribute('data-filtro-parametros') || '').split(',').forEach(function (nome) {
        if (nome) params.delete(nome);
      });
      params.delete('p');

      var nomeBusca = tabela.getAttribute('data-busca-parametro') || 'q';
      params.delete(nomeBusca);
      var busca = consulta.elements[nomeBusca];
      if (busca && busca.value.trim()) params.set(nomeBusca, busca.value.trim());

      tabela.querySelectorAll('input[data-tabela-filtro]:checked').forEach(function (opcao) {
        new URLSearchParams(opcao.value).forEach(function (valor, nome) {
          params.set(nome, valor);
        });
      });

      var texto = params.toString();
      window.location.assign(url.pathname + (texto ? '?' + texto : ''));
    }, true);
  }

  function iniciar() {
    document.querySelectorAll('dsgovbr-header').forEach(function (header) {
      quandoMontado(header, configurarBusca);
    });
    document.querySelectorAll('dsgovbr-tabela[data-dsgovbr-changelist]').forEach(ligarLista);
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', iniciar);
  } else {
    iniciar();
  }
})();
