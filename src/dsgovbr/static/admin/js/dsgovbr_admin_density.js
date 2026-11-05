// Densidade da tabela da lista do admin: "Alta" (.table-sm), "Média" (padrão)
// e "Baixa" (.dsgovbr-table-lg). Botões com data-density dentro de
// #density-toggle-group.
window.dsgovbrAdminDensityInit = function () {
  'use strict';

  var grupo = document.getElementById('density-toggle-group');
  var tabela = document.getElementById('result_list');
  if (!grupo || !tabela) return;

  var CLASSES = { small: 'table-sm', medium: '', large: 'dsgovbr-table-lg' };

  grupo.addEventListener('click', function (evento) {
    var botao = evento.target.closest('button[data-density]');
    if (!botao) return;
    Object.keys(CLASSES).forEach(function (chave) {
      if (CLASSES[chave]) tabela.classList.remove(CLASSES[chave]);
    });
    var classe = CLASSES[botao.getAttribute('data-density')];
    if (classe) tabela.classList.add(classe);
    grupo.querySelectorAll('button[data-density]').forEach(function (outro) {
      var ativo = outro === botao;
      outro.classList.toggle('active', ativo);
      outro.setAttribute('aria-pressed', ativo ? 'true' : 'false');
    });
  });
};

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', window.dsgovbrAdminDensityInit);
} else {
  window.dsgovbrAdminDensityInit();
}
