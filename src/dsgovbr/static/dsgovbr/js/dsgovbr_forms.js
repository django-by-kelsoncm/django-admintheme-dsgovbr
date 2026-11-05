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
      for (var i = 0; i < JA_ESTILIZADO.length; i++) {
        if (campo.classList.contains(JA_ESTILIZADO[i])) return;
      }
      classeDo(campo).forEach(function (classe) { campo.classList.add(classe); });
    });
  }

  window.dsgovbrBootstrapFields = aplicar;

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

  window.addEventListener('load', botoesDoAdmin);
  // O jQuery 3 executa o ready de forma assíncrona: registrar aqui, depois do
  // inlines.js, garante rodar após ele criar o "Adicionar outro".
  if (window.django && window.django.jQuery) {
    window.django.jQuery(botoesDoAdmin);
  }

  document.addEventListener('formset:added', function (evento) {
    aplicar(evento.target);
    botoesDoAdmin();
  });

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function () { aplicar(document); });
  } else {
    aplicar(document);
  }
})();
