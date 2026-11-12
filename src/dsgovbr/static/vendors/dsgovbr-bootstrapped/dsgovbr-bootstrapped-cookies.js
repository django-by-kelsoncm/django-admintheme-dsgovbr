/*!
 * dsgovbr-bootstrapped — consentimento de cookies: <dsgovbr-cookiebar> e API (opcional)
 * Licensed under MIT (https://github.com/abrasileirado/dsgovbr-bootstrapped/blob/main/LICENSE)
 */
// Barra de consentimento do GOV.BR DS: aviso no rodapé com "Gerenciar cookies",
// "Rejeitar cookies" e "Aceitar cookies"; configurações por grupo (switches) num
// modal do Bootstrap; e um botão flutuante que reabre as configurações depois da
// escolha. Sem dependência além do CSS do tema e do bootstrap.bundle (só para
// abrir o modal). Light DOM, como os demais web components do projeto.
//
//   <script src="dsgovbr-bootstrapped-cookies.js"></script>   <!-- no <head>, para a API estar pronta cedo -->
//
//   <dsgovbr-cookiebar declaracao="/cookies">
//     <dsgovbr-cookies-texto>Usamos cookies para melhorar sua experiência.</dsgovbr-cookies-texto>
//     <dsgovbr-cookies-grupo nome="desempenho" rotulo="Desempenho">Medem o uso do site.</dsgovbr-cookies-grupo>
//     <dsgovbr-cookies-grupo nome="funcionais" rotulo="Funcionais">Lembram suas preferências.</dsgovbr-cookies-grupo>
//   </dsgovbr-cookiebar>
//
// O grupo "estritamente necessários" (nome `necessarios`) é criado sozinho, sempre
// ativo e bloqueado; para trocar o texto dele, declare um <dsgovbr-cookies-grupo necessario>.
// A barra só aparece sem escolha salva (localStorage); depois dela aparece só o
// botão flutuante (`sem-botao` o desliga, para quem já tem outro acionador, como o do
// header). Atributos: `titulo` (padrão "Aviso de cookies"), `declaracao` (link da
// Declaração de Cookies) e `rotulo-declaracao`.
//
// API em `window.dsgovbrCookies` (funciona sem o elemento, ex.: para ligar scripts):
//   escolha()            -> { necessarios: true, desempenho: false, ... } ou null (sem escolha)
//   permitido("grupo")   -> true se a pessoa aceitou o grupo (necessarios é sempre true)
//   definir({grupo: bool}, origem?) grava a escolha e dispara o evento
//   limpar()             apaga a escolha (a barra volta)
//   abrir()              abre as configurações (exige o elemento e o bootstrap.bundle)
// Qualquer elemento com `data-dsgovbr-cookies-abrir` abre as configurações ao ser clicado
// (é o que o botão de ação rápida de <dsgovbr-header cookies> usa).
// Toda mudança dispara `dsgovbr:cookies` no <html>: `event.detail.grupos` (null depois
// de limpar) e `event.detail.origem` ("aceitar", "rejeitar", "salvar", "api" ou "limpar").
(function () {
  "use strict";

  var CHAVE = "dsgovbr-bootstrapped:cookies";
  var VERSAO = 1;
  var NOME_VALIDO = /^[a-z][a-z0-9_-]*$/i;
  var raiz = document.documentElement;

  // ----------------------------------------------------------------------- API
  function lerArmazenado() {
    try {
      var valor = JSON.parse(window.localStorage.getItem(CHAVE));
      if (valor && valor.v === VERSAO && valor.grupos && typeof valor.grupos === "object") {
        return valor.grupos;
      }
    } catch (e) {
      // modo privado, armazenamento bloqueado ou JSON inválido: sem escolha
    }
    return null;
  }

  function gravar(grupos) {
    try {
      window.localStorage.setItem(CHAVE, JSON.stringify({ v: VERSAO, grupos: grupos }));
    } catch (e) {
      // sem armazenamento: a escolha vale só para esta página
      memoria = grupos;
    }
  }

  function apagar() {
    memoria = null;
    try {
      window.localStorage.removeItem(CHAVE);
    } catch (e) {
      // nada a apagar
    }
  }

  var memoria = null; // escolha desta página quando o localStorage não grava

  function armazenado() {
    return lerArmazenado() || memoria;
  }

  function comNecessarios(grupos) {
    return Object.assign({ necessarios: true }, grupos, { necessarios: true });
  }

  function emitir(grupos, origem) {
    var detalhe = { grupos: grupos ? comNecessarios(grupos) : null, origem: origem };
    try {
      raiz.dispatchEvent(new CustomEvent("dsgovbr:cookies", { detail: detalhe }));
    } catch (e) {
      // navegador sem CustomEvent construtível: só não avisa
    }
  }

  var api = {
    escolha: function () {
      var grupos = armazenado();
      return grupos ? comNecessarios(grupos) : null;
    },

    permitido: function (grupo) {
      if (grupo === "necessarios") {
        return true;
      }
      var grupos = armazenado();
      return Boolean(grupos && grupos[grupo] === true);
    },

    definir: function (grupos, origem) {
      if (!grupos || typeof grupos !== "object") {
        throw new Error("dsgovbrCookies.definir: informe um objeto { grupo: true | false }");
      }
      var limpo = {};
      Object.keys(grupos).forEach(function (nome) {
        if (!NOME_VALIDO.test(nome)) {
          throw new Error('dsgovbrCookies.definir: nome de grupo inválido "' + nome + '"');
        }
        if (nome !== "necessarios") {
          limpo[nome] = grupos[nome] === true;
        }
      });
      gravar(limpo);
      emitir(limpo, origem || "api");
    },

    limpar: function () {
      apagar();
      emitir(null, "limpar");
    },

    abrir: function () {
      var el = document.querySelector("dsgovbr-cookiebar");
      if (!el || typeof el.abrir !== "function") {
        throw new Error("dsgovbrCookies.abrir: não há <dsgovbr-cookiebar> montado na página");
      }
      el.abrir();
    },
  };

  window.dsgovbrCookies = api;

  // Qualquer elemento com `data-dsgovbr-cookies-abrir` (ex.: o botão de ação rápida do
  // <dsgovbr-header cookies>) abre as configurações ao ser clicado. Delegação: vale
  // também para elementos criados depois do carregamento.
  var SELETOR_ABRIR = "[data-dsgovbr-cookies-abrir]";
  document.addEventListener("click", function (evento) {
    var alvo = evento.target && evento.target.closest ? evento.target.closest(SELETOR_ABRIR) : null;
    if (!alvo) {
      return;
    }
    evento.preventDefault();
    try {
      api.abrir();
    } catch (erro) {
      console.error(erro.message);
    }
  });

  // ------------------------------------------------------------------ elemento
  if (!window.customElements) {
    return; // navegador sem custom elements: só a API fica disponível
  }

  var contador = 0;

  // Monta um elemento só com a API de DOM: valores de atributo e texto nunca viram HTML.
  function h(tag, atributos, filhos) {
    var el = document.createElement(tag);
    Object.keys(atributos || {}).forEach(function (nome) {
      var valor = atributos[nome];
      if (valor !== null && valor !== undefined && valor !== false) {
        el.setAttribute(nome, valor === true ? "" : valor);
      }
    });
    [].concat(filhos === undefined ? [] : filhos).forEach(function (filho) {
      if (filho !== null && filho !== undefined && filho !== false) {
        el.append(filho);
      }
    });
    return el;
  }

  function texto(el) {
    return (el.textContent || "").replace(/\s+/g, " ").trim();
  }

  // Filhos diretos com a tag (ex.: "dsgovbr-cookies-grupo").
  function filhos(host, tag) {
    return Array.prototype.filter.call(host.children, function (el) {
      return el.localName === tag;
    });
  }

  var TEXTO_PADRAO = "Usamos cookies para melhorar sua experiência e analisar o uso do site. Você pode escolher quais aceitar.";
  var NECESSARIOS = {
    nome: "necessarios",
    rotulo: "Estritamente necessários",
    descricao: "Essenciais ao funcionamento do site; ficam sempre ativos.",
    necessario: true,
  };

  class Cookiebar extends HTMLElement {
    static get observedAttributes() {
      return ["titulo", "declaracao", "rotulo-declaracao", "sem-botao"];
    }

    connectedCallback() {
      var self = this;
      function iniciar() {
        if (!self.isConnected) {
          return;
        }
        if (!self._montado) {
          self._modelo = self.ler();
          self._montado = true;
          self.montar();
          self.setAttribute("data-dsgovbr-montado", "");
        }
        self.ouvir();
      }
      // Antes do parser terminar os filhos ainda não existem.
      if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", iniciar, { once: true });
      } else {
        iniciar();
      }
    }

    disconnectedCallback() {
      if (this._ouvinte) {
        raiz.removeEventListener("dsgovbr:cookies", this._ouvinte);
        this._ouvinte = null;
      }
    }

    attributeChangedCallback(nome, antigo, novo) {
      if (this._montado && antigo !== novo) {
        this.montar();
      }
    }

    attr(nome, padrao) {
      return this.hasAttribute(nome) ? this.getAttribute(nome) : padrao;
    }

    ler() {
      var grupos = filhos(this, "dsgovbr-cookies-grupo")
        .map(function (el) {
          return {
            nome: el.getAttribute("nome") || "",
            rotulo: el.getAttribute("rotulo") || el.getAttribute("nome") || "",
            descricao: texto(el),
            necessario: el.hasAttribute("necessario"),
          };
        })
        .filter(function (g) {
          var ok = NOME_VALIDO.test(g.nome) || g.necessario;
          if (!ok) {
            console.error('dsgovbr-cookiebar: grupo com "nome" inválido ou ausente foi ignorado', g);
          }
          return ok;
        })
        .map(function (g) {
          return g.necessario ? Object.assign(g, { nome: "necessarios" }) : g;
        });
      if (!grupos.some(function (g) { return g.necessario; })) {
        grupos.unshift(NECESSARIOS);
      }
      var texto_ = filhos(this, "dsgovbr-cookies-texto");
      return {
        grupos: grupos,
        textoNos: texto_.length ? Array.prototype.slice.call(texto_[0].childNodes) : [],
      };
    }

    montar() {
      var self = this;
      var id = this._uid || (this._uid = "dsgovbr-cookiebar-" + (contador += 1));
      var titulo = this.attr("titulo", "Aviso de cookies");
      var declaracao = this.attr("declaracao", "");
      var grupos = this._modelo.grupos;
      var opcionais = grupos.filter(function (g) { return !g.necessario; });

      var texto_ = this._modelo.textoNos.length ? this._modelo.textoNos : [document.createTextNode(TEXTO_PADRAO)];
      var paragrafo = h("p", {}, texto_.concat(
        declaracao ? [document.createTextNode(" "), h("a", { href: declaracao }, this.attr("rotulo-declaracao", "Declaração de Cookies"))] : []
      ));

      function botao(classe, rotulo, acao) {
        var b = h("button", { type: "button", class: "btn " + classe }, rotulo);
        b.addEventListener("click", acao);
        return b;
      }

      // Não bloqueia a página: é um aviso, não um diálogo. Por isso não usa .offcanvas
      // (o Bootstrap abre sozinho todo .offcanvas.show, com backdrop e prisão de foco).
      this._barra = h("section", { class: "fixed-bottom bg-body py-3 dsgovbr-cookiebar-barra", role: "region", "aria-labelledby": id + "-titulo" },
          h("div", { class: "container-lg" }, [
            h("h2", { class: "offcanvas-title mb-2", id: id + "-titulo" }, titulo),
            paragrafo,
            h("div", { class: "d-flex flex-wrap justify-content-end gap-3" }, [
              botao("btn-outline-primary", "Gerenciar cookies", function () { self.abrir(); }),
              botao("btn-outline-primary", "Rejeitar cookies", function () { self.escolher(false, "rejeitar"); }),
              botao("btn-primary", "Aceitar cookies", function () { self.escolher(true, "aceitar"); }),
            ]),
          ])
      );

      this._interruptores = {};
      var lista = grupos.map(function (g) {
        var idCampo = id + "-grupo-" + g.nome;
        var campo = h("input", {
          class: "form-check-input", type: "checkbox", role: "switch", id: idCampo, name: g.nome,
          "aria-describedby": g.descricao ? idCampo + "-descricao" : false,
          checked: g.necessario, disabled: g.necessario,
        });
        self._interruptores[g.nome] = campo;
        return h("div", { class: "form-check form-switch mb-3" }, [
          campo,
          h("label", { class: "form-check-label", for: idCampo }, g.rotulo),
          g.descricao ? h("div", { class: "form-text", id: idCampo + "-descricao" }, g.descricao) : null,
        ]);
      });

      this._modal = h("div", { class: "modal fade", tabindex: "-1", id: id + "-modal", "aria-labelledby": id + "-modal-titulo" },
        h("div", { class: "modal-dialog modal-dialog-scrollable" },
          h("div", { class: "modal-content" }, [
            h("div", { class: "modal-header" }, [
              h("h2", { class: "modal-title", id: id + "-modal-titulo" }, "Configurações de cookies"),
              h("button", { type: "button", class: "btn-close", "data-bs-dismiss": "modal", "aria-label": "Fechar" }),
            ]),
            h("div", { class: "modal-body" }, lista),
            h("div", { class: "modal-footer" }, [
              botao("btn-outline-primary", "Rejeitar cookies", function () { self.escolher(false, "rejeitar"); }),
              botao("btn-primary", "Salvar", function () {
                var escolha = {};
                opcionais.forEach(function (g) { escolha[g.nome] = self._interruptores[g.nome].checked; });
                api.definir(escolha, "salvar");
                self.fecharModal();
              }),
            ]),
          ])
        )
      );

      this._botao = h("button", { type: "button", class: "btn btn-primary rounded-circle dsgovbr-cookiebar-botao", "aria-label": "Configurações de cookies", title: "Configurações de cookies" },
        h("i", { class: "fas fa-cookie-bite", "aria-hidden": "true" }));
      this._botao.addEventListener("click", function () { self.abrir(); });

      this.replaceChildren(this._barra, this._botao, this._modal);
      this.atualizar();
    }

    // Reflete a escolha salva: barra sem escolha, botão flutuante com escolha.
    atualizar() {
      var escolha = armazenado();
      this._barra.hidden = Boolean(escolha);
      this._botao.hidden = !escolha || this.hasAttribute("sem-botao");
      var interruptores = this._interruptores;
      Object.keys(interruptores).forEach(function (nome) {
        if (nome !== "necessarios") {
          interruptores[nome].checked = Boolean(escolha && escolha[nome] === true);
        }
      });
    }

    ouvir() {
      var self = this;
      if (!this._ouvinte) {
        this._ouvinte = function () { self.atualizar(); };
        raiz.addEventListener("dsgovbr:cookies", this._ouvinte);
      }
      this.atualizar();
    }

    // Aceitar ou rejeitar todos os grupos opcionais.
    escolher(aceitar, origem) {
      var escolha = {};
      this._modelo.grupos.forEach(function (g) {
        if (!g.necessario) {
          escolha[g.nome] = aceitar;
        }
      });
      var tinhaModal = this._modal.classList.contains("show");
      api.definir(escolha, origem);
      if (tinhaModal) {
        this.fecharModal();
      } else {
        this.focarAcionador();
      }
    }

    // Depois da escolha a barra some: o foco vai ao botão flutuante ou, sem ele, ao
    // primeiro acionador visível da página (ex.: o botão do header).
    focarAcionador() {
      var alvo = this._botao.hidden
        ? Array.prototype.find.call(document.querySelectorAll(SELETOR_ABRIR), function (el) { return el.offsetParent !== null; })
        : this._botao;
      if (alvo) {
        alvo.focus();
      }
    }

    abrir() {
      var bs = window.bootstrap;
      if (!bs || !bs.Modal) {
        throw new Error("dsgovbr-cookiebar: carregue o bootstrap.bundle para abrir as configurações");
      }
      this.atualizar();
      bs.Modal.getOrCreateInstance(this._modal).show();
    }

    // O foco volta ao botão flutuante: o botão que abriu o modal pode ter sumido (a barra).
    fecharModal() {
      var self = this;
      var bs = window.bootstrap;
      if (!bs || !bs.Modal) {
        return;
      }
      this._modal.addEventListener("hidden.bs.modal", function () {
        self.focarAcionador();
      }, { once: true });
      bs.Modal.getOrCreateInstance(this._modal).hide();
    }
  }

  // Elementos-dado: só carregam atributos e conteúdo para o <dsgovbr-cookiebar>, que
  // os troca pelo HTML final (o CSS os oculta se sobrarem fora dele).
  ["dsgovbr-cookies-grupo", "dsgovbr-cookies-texto"].forEach(function (nome) {
    if (!window.customElements.get(nome)) {
      window.customElements.define(nome, class extends HTMLElement {});
    }
  });

  if (!window.customElements.get("dsgovbr-cookiebar")) {
    window.customElements.define("dsgovbr-cookiebar", Cookiebar);
  }
})();
