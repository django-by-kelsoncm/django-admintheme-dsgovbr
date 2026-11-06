/*!
 * dsgovbr-bootstraped — seletor de modo claro/escuro (opcional)
 * Licensed under MIT (https://github.com/abrasileirado/dsgovbr-bootstraped/blob/main/LICENSE)
 */
// Aplica o modo claro ou escuro pelo `data-bs-theme` do <html>, que o Bootstrap
// 5.3 e o dsgovbr-bootstraped já sabem pintar. Não depende de nada.
//
// Carregue de forma síncrona no <head>, depois do CSS: assim o modo é aplicado
// antes da primeira pintura, sem "piscar" o claro.
//
//   <script src="dsgovbr-bootstraped-modo.js"></script>
//   <button type="button" data-dsgovbr-modo aria-label="Modo escuro">…</button>
//
// Preferência: escolha salva no localStorage > `prefers-color-scheme` do sistema.
// Todo elemento com `data-dsgovbr-modo` alterna entre claro e escuro ao ser
// clicado e tem o `aria-pressed` mantido em dia ("true" no escuro). Com
// `data-dsgovbr-modo="light"` ou `"dark"`, o clique fixa esse modo.
//
// API em `window.dsgovbrModo`: `atual()`, `aplicar(modo)` e `alternar()`. Toda
// troca dispara o evento `dsgovbr:modo` no <html> (`event.detail.modo`).
(function () {
  "use strict";

  var CHAVE = "dsgovbr-bootstraped:modo";
  var MODOS = ["light", "dark"];
  var SELETOR = "[data-dsgovbr-modo]";
  var raiz = document.documentElement;
  var sistema = window.matchMedia ? window.matchMedia("(prefers-color-scheme: dark)") : null;

  function lerArmazenado() {
    try {
      var valor = window.localStorage.getItem(CHAVE);
      return MODOS.indexOf(valor) !== -1 ? valor : null;
    } catch (e) {
      return null; // modo privado ou armazenamento bloqueado
    }
  }

  function gravar(modo) {
    try {
      window.localStorage.setItem(CHAVE, modo);
    } catch (e) {
      // sem armazenamento: a escolha vale só para esta página
    }
  }

  function doSistema() {
    return sistema && sistema.matches ? "dark" : "light";
  }

  function atual() {
    return raiz.getAttribute("data-bs-theme") === "dark" ? "dark" : "light";
  }

  function sincronizarBotoes() {
    var escuro = String(atual() === "dark");
    var botoes = document.querySelectorAll(SELETOR);
    for (var i = 0; i < botoes.length; i++) {
      botoes[i].setAttribute("aria-pressed", escuro);
    }
  }

  function definir(modo) {
    if (MODOS.indexOf(modo) === -1) {
      throw new Error('dsgovbrModo: modo inválido "' + modo + '" (use "light" ou "dark")');
    }
    raiz.setAttribute("data-bs-theme", modo);
    sincronizarBotoes();
    var evento;
    try {
      evento = new CustomEvent("dsgovbr:modo", { detail: { modo: modo } });
    } catch (e) {
      return; // navegador sem CustomEvent construtível: só não avisa
    }
    raiz.dispatchEvent(evento);
  }

  function aplicar(modo) {
    definir(modo);
    gravar(modo);
  }

  function alternar() {
    aplicar(atual() === "dark" ? "light" : "dark");
  }

  // Antes da primeira pintura.
  definir(lerArmazenado() || doSistema());

  // Sem escolha salva, acompanha a troca de tema do sistema.
  if (sistema) {
    var mudou = function () {
      if (!lerArmazenado()) {
        definir(doSistema());
      }
    };
    if (sistema.addEventListener) {
      sistema.addEventListener("change", mudou);
    } else if (sistema.addListener) {
      sistema.addListener(mudou);
    }
  }

  // Delegação: vale também para botões criados depois do carregamento.
  document.addEventListener("click", function (evento) {
    var alvo = evento.target && evento.target.closest ? evento.target.closest(SELETOR) : null;
    if (!alvo) {
      return;
    }
    evento.preventDefault();
    var fixo = alvo.getAttribute("data-dsgovbr-modo");
    if (MODOS.indexOf(fixo) !== -1) {
      aplicar(fixo);
    } else {
      alternar();
    }
  });

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", sincronizarBotoes);
  } else {
    sincronizarBotoes();
  }

  window.dsgovbrModo = { atual: atual, aplicar: aplicar, alternar: alternar };
})();
