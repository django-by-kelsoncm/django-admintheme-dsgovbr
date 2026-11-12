/*!
 * dsgovbr-bootstraped — web components de header, menu, footer, breadcrumb, paginação, modal, campo e tabela (opcional)
 * Licensed under MIT (https://github.com/abrasileirado/dsgovbr-bootstraped/blob/main/LICENSE)
 */
// Custom elements em light DOM (sem Shadow DOM): geram as mesmas classes
// Bootstrap das composições documentadas, então o CSS do tema vale sem ajuste e
// o seu CSS também. Não dependem de nada além do CSS do tema; o JS do Bootstrap
// (bootstrap.bundle) é quem abre o menu, os dropdowns e a busca (data-bs-*).
//
//   <script src="dsgovbr-bootstraped-componentes.js" defer></script>
//
// Elementos: <dsgovbr-breadcrumb>, <dsgovbr-menu>, <dsgovbr-footer>,
// <dsgovbr-header>, <dsgovbr-paginacao>, <dsgovbr-modal>, <dsgovbr-campo> e
// <dsgovbr-tabela>. Cada um lê os filhos e atributos UMA vez, ao conectar, e
// troca o conteúdo pelo HTML final (o conteúdo original é só a declaração).
// Mudar um atributo depois remonta o componente. O modo claro/escuro continua
// no JS à parte (dsgovbr-bootstraped-modo.js); o header só renderiza o botão.
//
// Filhos declarativos: o pai lê elementos-dado (<dsgovbr-item>, <dsgovbr-pasta>,
// <dsgovbr-coluna>, <dsgovbr-rede>, <dsgovbr-logo>, <dsgovbr-aviso>...) e os troca
// pelo HTML final; eles não renderizam nada sozinhos (o CSS os oculta fora de um
// componente). `icone="fas fa-home"` são as classes do ícone. Onde se espera um
// <dsgovbr-item>, um <a href> comum também vale.
(function () {
  "use strict";

  if (!window.customElements) {
    return; // navegador sem custom elements: a página fica sem os componentes
  }

  var contador = 0;

  function proximoId(prefixo) {
    contador += 1;
    return "dsgovbr-" + prefixo + "-" + contador;
  }

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

  function icone(classes, extra) {
    return classes ? h("i", { class: classes + (extra ? " " + extra : ""), "aria-hidden": "true" }) : null;
  }

  function texto(el) {
    return (el.textContent || "").replace(/\s+/g, " ").trim();
  }

  // Filhos diretos com um dos nomes de tag (ex.: "dsgovbr-pasta").
  function filhos(raiz, tags) {
    var nomes = [].concat(tags);
    return Array.prototype.filter.call(raiz.children, function (el) {
      return nomes.indexOf(el.localName) !== -1;
    });
  }

  function ehItem(el) {
    return el.localName === "dsgovbr-item" || el.localName === "a";
  }

  // <dsgovbr-item href icone atual externo>Texto</dsgovbr-item> (ou <a>) -> dados simples.
  function lerLink(a) {
    return {
      href: a.getAttribute("href") || "#",
      texto: texto(a),
      icone: a.getAttribute("icone"),
      atual: a.hasAttribute("atual"),
      externo: a.hasAttribute("externo"),
    };
  }

  // Itens (<dsgovbr-item> ou <a>) filhos diretos de um elemento.
  function lerItens(raiz) {
    return Array.prototype.filter.call(raiz.children, ehItem).map(lerLink);
  }

  // Nós de dentro do primeiro filho com a tag (HTML livre), ou [].
  function nosDe(raiz, tag) {
    var achados = filhos(raiz, tag);
    return achados.length ? Array.prototype.slice.call(achados[0].childNodes) : [];
  }

  function lerRede(el) {
    return { href: el.getAttribute("href") || "#", texto: texto(el), icone: el.getAttribute("icone") };
  }

  function modoEscuro() {
    return document.documentElement.getAttribute("data-bs-theme") === "dark";
  }

  // Base: lê uma vez, monta ao conectar e remonta se um atributo mudar.
  // Se o script rodar antes do parser terminar, espera o DOMContentLoaded: sem
  // isso o connectedCallback chegaria antes dos filhos existirem.
  class Base extends HTMLElement {
    connectedCallback() {
      var self = this;
      function iniciar() {
        if (!self.isConnected || self._montado) {
          return;
        }
        self._modelo = self.ler();
        self._montado = true;
        self.montar();
        self.setAttribute("data-dsgovbr-montado", "");
      }
      if (document.readyState === "loading") {
        document.addEventListener("DOMContentLoaded", iniciar, { once: true });
      } else {
        iniciar();
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
  }

  // ---------------------------------------------------------------- breadcrumb
  // <dsgovbr-breadcrumb rotulo="Trilha de navegação" compacto>
  //   <dsgovbr-item href="/">Início</dsgovbr-item>
  //   <dsgovbr-item href="/x">Cadastros</dsgovbr-item>
  //   <dsgovbr-item>Usuários</dsgovbr-item>
  // </dsgovbr-breadcrumb>
  // O último item é a página atual (aria-current="page"), mesmo sendo um link.
  class Breadcrumb extends Base {
    static get observedAttributes() {
      return ["rotulo", "compacto"];
    }

    ler() {
      return Array.prototype.map.call(this.children, function (el) {
        return { href: ehItem(el) ? el.getAttribute("href") : null, texto: texto(el) };
      });
    }

    montar() {
      var itens = this._modelo;
      var ultimo = itens.length - 1;
      var lista = h(
        "ol",
        { class: "breadcrumb" + (this.hasAttribute("compacto") ? " mb-1" : "") },
        itens.map(function (item, i) {
          if (i === ultimo) {
            return h("li", { class: "breadcrumb-item active", "aria-current": "page" }, item.texto);
          }
          return h("li", { class: "breadcrumb-item" }, item.href ? h("a", { href: item.href }, item.texto) : item.texto);
        })
      );
      this.replaceChildren(h("nav", { "aria-label": this.attr("rotulo", "Trilha de navegação") }, lista));
    }
  }

  // ---------------------------------------------------------------------- menu
  // O próprio elemento é o offcanvas (.offcanvas.offcanvas-start): o `id` dele é
  // o alvo do botão de abrir (<dsgovbr-header menu="id">).
  //
  // <dsgovbr-menu id="menu-principal" titulo="Sistema" logo="logo.svg">
  //   <dsgovbr-item href="/" icone="fas fa-home">Início</dsgovbr-item>
  //   <dsgovbr-pasta rotulo="Cadastros" icone="fas fa-users" aberta id="menu-cadastros">
  //     <dsgovbr-item href="/usuarios" icone="fas fa-user" atual>Usuários</dsgovbr-item>
  //   </dsgovbr-pasta>
  //   <dsgovbr-menu-rodape rotulo-redes="Redes sociais">
  //     <dsgovbr-logo src="orgao.svg" alt="Logo do órgão"></dsgovbr-logo>
  //     <dsgovbr-item href="https://..." externo>Portal do órgão</dsgovbr-item>
  //     <dsgovbr-rede href="https://..." icone="fab fa-youtube">YouTube</dsgovbr-rede>
  //     <dsgovbr-aviso>Licença <strong>CC BY 4.0</strong>.</dsgovbr-aviso>
  //   </dsgovbr-menu-rodape>
  // </dsgovbr-menu>
  class Menu extends Base {
    static get observedAttributes() {
      return ["titulo", "logo", "rotulo", "rotulo-fechar"];
    }

    ler() {
      var itens = [];
      Array.prototype.forEach.call(this.children, function (el) {
        if (ehItem(el)) {
          itens.push({ tipo: "link", link: lerLink(el) });
        } else if (el.localName === "dsgovbr-pasta") {
          itens.push({
            tipo: "pasta",
            id: el.id || null,
            rotulo: el.getAttribute("rotulo") || "",
            icone: el.getAttribute("icone"),
            aberta: el.hasAttribute("aberta"),
            links: lerItens(el),
          });
        }
      });
      var rodape = filhos(this, "dsgovbr-menu-rodape")[0];
      return {
        itens: itens,
        rodape: rodape && {
          rotuloRedes: rodape.getAttribute("rotulo-redes") || "Redes sociais",
          logos: filhos(rodape, "dsgovbr-logo").map(function (l) { return { src: l.getAttribute("src") || "", alt: l.getAttribute("alt") || "" }; }),
          links: lerItens(rodape),
          redes: filhos(rodape, "dsgovbr-rede").map(lerRede),
          avisoNos: nosDe(rodape, "dsgovbr-aviso"),
        },
      };
    }

    montar() {
      var id = this.id || (this.id = proximoId("menu"));
      var idTitulo = id + "-titulo";
      var titulo = this.attr("titulo", "");
      var logo = this.attr("logo", "");
      this.classList.add("offcanvas", "offcanvas-start");
      this.setAttribute("tabindex", "-1");
      this.setAttribute("aria-labelledby", idTitulo);

      function link(l) {
        return h(
          "a",
          { class: "list-group-item list-group-item-action" + (l.atual ? " active" : ""), href: l.href, "aria-current": l.atual ? "page" : false },
          [icone(l.icone), l.texto]
        );
      }

      var lista = h("div", { class: "list-group list-group-flush" });
      this._modelo.itens.forEach(function (item, i) {
        if (item.tipo === "link") {
          lista.append(link(item.link));
          return;
        }
        var alvo = item.id || id + "-pasta-" + (i + 1);
        lista.append(
          h(
            "button",
            { class: "list-group-item list-group-item-action", type: "button", "data-bs-toggle": "collapse", "data-bs-target": "#" + alvo, "aria-expanded": String(item.aberta), "aria-controls": alvo },
            [icone(item.icone), item.rotulo]
          ),
          h("div", { class: "collapse" + (item.aberta ? " show" : ""), id: alvo }, h("div", { class: "list-group list-group-flush" }, item.links.map(link)))
        );
      });

      var cabecalho = h("div", { class: "offcanvas-header" }, [
        h("div", { class: "d-flex align-items-center gap-2 me-auto" }, [
          logo ? h("img", { src: logo, height: "40", alt: "" }) : null,
          h("span", { id: idTitulo }, titulo),
        ]),
        h("button", { type: "button", class: "btn btn-link rounded-circle", "data-bs-dismiss": "offcanvas", "aria-label": this.attr("rotulo-fechar", "Fechar o menu") }, icone("fas fa-times")),
      ]);

      var corpo = h("div", { class: "offcanvas-body d-flex flex-column p-0" }, h("nav", { "aria-label": this.attr("rotulo", "Menu principal") }, lista));
      var rodape = this._modelo.rodape;
      if (rodape && (rodape.logos.length || rodape.links.length || rodape.redes.length || rodape.avisoNos.length)) {
        var partes = [];
        if (rodape.logos.length) {
          partes.push(h("div", { class: "d-flex gap-3 px-5 py-2 border-top border-bottom" },
            rodape.logos.map(function (l) { return h("img", { src: l.src, height: "33", alt: l.alt }); })));
        }
        if (rodape.links.length) {
          partes.push(h("div", { class: "px-5 py-3 border-bottom" }, rodape.links.map(function (l, i) {
            return h("a", { class: "d-block text-decoration-none" + (i < rodape.links.length - 1 ? " mb-3" : ""), href: l.href },
              [l.texto, l.externo ? icone("fas fa-external-link-square-alt", "ms-1") : null]);
          })));
        }
        if (rodape.redes.length) {
          partes.push(h("div", { class: "px-5 py-2 border-bottom" }, [
            h("p", { class: "fw-semibold mb-1" }, rodape.rotuloRedes),
            h("div", { class: "d-flex" }, rodape.redes.map(function (r) {
              return h("a", { class: "btn btn-link rounded-circle", href: r.href, "aria-label": r.texto }, icone(r.icone));
            })),
          ]));
        }
        if (rodape.avisoNos.length) {
          partes.push(h("p", { class: "small text-center p-3 m-0" }, rodape.avisoNos));
        }
        corpo.append(h("div", { class: "mt-auto" }, partes));
      }
      this.replaceChildren(cabecalho, corpo);
    }
  }

  // -------------------------------------------------------------------- footer
  // <dsgovbr-footer logo="logo-negativo.svg" logo-alt="Logo do sistema"
  //                 assinatura="assinatura.svg" assinatura-alt="Assinatura do órgão">
  //   <dsgovbr-coluna titulo="Sistema"><dsgovbr-item href="/sobre">Sobre</dsgovbr-item>…</dsgovbr-coluna>
  //   <dsgovbr-rede href="…" icone="fab fa-facebook-f">Facebook</dsgovbr-rede>
  //   <dsgovbr-aviso>Texto legal (aceita HTML)</dsgovbr-aviso>
  // </dsgovbr-footer>
  // Fica sempre no modo escuro (data-bs-theme="dark"), como no GOV.BR DS.
  class Footer extends Base {
    static get observedAttributes() {
      return ["logo", "logo-alt", "assinatura", "assinatura-alt", "rotulo-redes"];
    }

    ler() {
      return {
        colunas: filhos(this, "dsgovbr-coluna").map(function (col) {
          return {
            titulo: col.getAttribute("titulo") || "",
            links: lerItens(col),
          };
        }),
        redes: filhos(this, "dsgovbr-rede").map(lerRede),
        avisoNos: nosDe(this, "dsgovbr-aviso"),
      };
    }

    montar() {
      var m = this._modelo;
      var logo = this.attr("logo", "");
      var assinatura = this.attr("assinatura", "");
      var partes = [];
      if (logo) {
        partes.push(h("img", { class: "d-block mb-5", src: logo, height: "48", alt: this.attr("logo-alt", "") }));
      }
      if (m.colunas.length) {
        partes.push(
          h(
            "div",
            { class: "row g-0 pb-5" },
            m.colunas.map(function (col) {
              return h("div", { class: "col-6 col-md-3 col-lg-2" }, [
                h("h2", {}, col.titulo),
                h(
                  "nav",
                  { class: "nav flex-column", "aria-label": col.titulo },
                  col.links.map(function (l) { return h("a", { class: "nav-link", href: l.href }, l.texto); })
                ),
              ]);
            })
          )
        );
      }
      if (m.redes.length || assinatura) {
        partes.push(
          h("div", { class: "row align-items-end justify-content-between pb-5 d-none d-sm-flex" }, [
            h(
              "div",
              { class: "col" },
              m.redes.length
                ? [
                    h("p", { class: "fs-6 fw-bolder text-uppercase mb-4" }, this.attr("rotulo-redes", "Redes sociais")),
                    h(
                      "div",
                      { class: "d-flex gap-3" },
                      m.redes.map(function (r) {
                        return h("a", { class: "btn btn-link rounded-circle", href: r.href, "aria-label": r.texto }, icone(r.icone));
                      })
                    ),
                  ]
                : []
            ),
            h("div", { class: "col text-end" }, assinatura ? h("img", { src: assinatura, height: "46", alt: this.attr("assinatura-alt", "") }) : null),
          ])
        );
      }
      var filhos = [h("div", { class: "container-lg" }, partes)];
      if (m.avisoNos.length) {
        filhos.push(
          h("hr", { class: "my-3" }),
          h("div", { class: "container-lg" }, h("p", { class: "small fw-medium text-center pb-3 m-0" }, m.avisoNos))
        );
      }
      this.replaceChildren(h("footer", { class: "bg-body", "data-bs-theme": "dark" }, filhos));
    }
  }

  // -------------------------------------------------------------------- header
  // <dsgovbr-header logo="logo.svg" logo-alt="Página inicial" href="/"
  //                 assinatura="Ministério Exemplo"
  //                 titulo="Sistema" subtitulo="Gestão de usuários"
  //                 menu="menu-principal" busca modo cookies usuario="Maria Silva"
  //                 pagina="Usuários">
  //   <dsgovbr-acesso-rapido><dsgovbr-item href="/docs">Documentação</dsgovbr-item></dsgovbr-acesso-rapido>
  //   <dsgovbr-funcionalidades><dsgovbr-item href="#" icone="fas fa-headset">Suporte</dsgovbr-item></dsgovbr-funcionalidades>
  //   <dsgovbr-usuario-menu>
  //     <dsgovbr-item href="/perfil">Meu perfil</dsgovbr-item> <dsgovbr-divisor></dsgovbr-divisor>
  //     <dsgovbr-item href="/sair">Sair</dsgovbr-item>
  //   </dsgovbr-usuario-menu>
  //   <dsgovbr-breadcrumb>…</dsgovbr-breadcrumb>
  //   <dsgovbr-acoes><button class="btn btn-primary">Adicionar</button></dsgovbr-acoes>
  // </dsgovbr-header>
  // O <header> traz logo, ações, título do sistema e busca. O breadcrumb, o título
  // da página e as ações ficam numa barra logo abaixo dele, fora do <header>, e
  // as duas grudam juntas no topo (.sticky-top); `estatico` desliga a fixação.
  // O host usa `display: contents` (ver o CSS do tema), então o wrapper gerado é
  // que gruda no topo, relativo ao <body>.
  //
  // Ao rolar a página, a linha de cima (logo, assinatura e ações) some e fica só a
  // do título e da busca, sem o subtítulo (atributo data-dsgovbr-rolado no host; o CSS faz o resto).
  // Há histerese (recolhe depois de 100px, volta com menos de 20px) e páginas
  // curtas não recolhem, para a mudança de altura não gerar vai-e-volta.
  class Header extends Base {
    static get observedAttributes() {
      return ["logo", "logo-alt", "href", "assinatura", "titulo", "subtitulo", "menu", "busca", "modo", "cookies", "usuario", "pagina", "estatico"];
    }

    connectedCallback() {
      super.connectedCallback();
      if (this._montado) {
        this.ouvirRolagem();
      }
    }

    disconnectedCallback() {
      this.pararRolagem();
    }

    ouvirRolagem() {
      var self = this;
      this.pararRolagem();
      if (this.hasAttribute("estatico")) {
        this.removeAttribute("data-dsgovbr-rolado");
        return;
      }
      var agendado = false;
      function atualizar() {
        agendado = false;
        var rolado = self.hasAttribute("data-dsgovbr-rolado");
        var y = window.pageYOffset;
        var sobra = document.documentElement.scrollHeight - window.innerHeight;
        if (!rolado && y > 100 && sobra > 300) {
          self.setAttribute("data-dsgovbr-rolado", "");
        } else if (rolado && y < 20) {
          self.removeAttribute("data-dsgovbr-rolado");
        }
      }
      this._rolagem = function () {
        if (!agendado) {
          agendado = true;
          window.requestAnimationFrame(atualizar);
        }
      };
      window.addEventListener("scroll", this._rolagem, { passive: true });
      atualizar();
    }

    pararRolagem() {
      if (this._rolagem) {
        window.removeEventListener("scroll", this._rolagem);
        this._rolagem = null;
      }
    }

    itensDe(tag) {
      var grupo = filhos(this, tag)[0];
      return grupo ? lerItens(grupo) : [];
    }

    ler() {
      return {
        acessoRapido: this.itensDe("dsgovbr-acesso-rapido"),
        funcionalidades: this.itensDe("dsgovbr-funcionalidades"),
        // item -> link; <dsgovbr-divisor> (ou <hr>) -> null, vira divisor
        usuario: (function (menu) {
          return menu
            ? Array.prototype.filter.call(menu.children, function (el) { return ehItem(el) || el.localName === "dsgovbr-divisor" || el.localName === "hr"; })
                .map(function (el) { return ehItem(el) ? lerLink(el) : null; })
            : [];
        })(filhos(this, "dsgovbr-usuario-menu")[0]),
        breadcrumb: filhos(this, "dsgovbr-breadcrumb"),
        acoes: nosDe(this, "dsgovbr-acoes"),
      };
    }

    montar() {
      var m = this._modelo;
      var id = this._uid || (this._uid = proximoId("header"));
      var href = this.attr("href", "#");
      var logo = this.attr("logo", "");
      var assinatura = this.attr("assinatura", "");
      var titulo = this.attr("titulo", "");
      var subtitulo = this.attr("subtitulo", "");
      var menu = this.attr("menu", "");
      var busca = this.hasAttribute("busca");
      var modo = this.hasAttribute("modo");
      var cookies = this.hasAttribute("cookies");
      var usuario = this.attr("usuario", "");
      var pagina = this.attr("pagina", "");
      var idBusca = id + "-busca";
      var botaoRedondo = "btn btn-link btn-sm rounded-circle";

      function botaoModo(classe, extra) {
        return h(
          "button",
          Object.assign({ class: classe, type: "button", "data-dsgovbr-modo": true, "aria-pressed": String(modoEscuro()) }, extra),
          null
        );
      }

      // dropdown do celular: botão + menu
      function dropdown(rotuloBotao, iconeBotao, cabecalho, itens, classe) {
        return h("div", { class: "dropdown " + classe }, [
          h("button", { class: botaoRedondo, type: "button", "data-bs-toggle": "dropdown", "aria-expanded": "false", "aria-label": rotuloBotao }, icone(iconeBotao)),
          h("ul", { class: "dropdown-menu dropdown-menu-end" }, [h("li", {}, h("h2", { class: "dropdown-header" }, cabecalho))].concat(itens)),
        ]);
      }

      var cima = h("div", { class: "dsgovbr-header-topo d-flex align-items-center gap-3" }, [
        logo ? h("a", { href: href }, h("img", { src: logo, height: "40", alt: this.attr("logo-alt", "") })) : null,
        assinatura ? h("div", { class: "vr d-none d-sm-block" }) : null,
        assinatura ? h("span", { class: "navbar-text p-0 fw-medium d-none d-sm-block" }, assinatura) : null,
      ]);

      var acoesTopo = h("div", { class: "d-flex align-items-center gap-1 ms-auto" });

      if (m.acessoRapido.length) {
        acoesTopo.append(
          h(
            "ul",
            { class: "navbar-nav flex-row d-none d-xl-flex", "aria-label": "Acesso rápido" },
            m.acessoRapido.map(function (l) { return h("li", { class: "nav-item" }, h("a", { class: "nav-link px-2", href: l.href }, l.texto)); })
          ),
          dropdown(
            "Abrir acesso rápido",
            "fas fa-ellipsis-v",
            "Acesso rápido",
            m.acessoRapido.map(function (l) { return h("li", {}, h("a", { class: "dropdown-item", href: l.href }, l.texto)); }),
            "d-xl-none"
          )
        );
      }

      if (m.funcionalidades.length || modo || cookies) {
        if (m.acessoRapido.length) {
          acoesTopo.append(h("div", { class: "vr mx-1" }));
        }
        var desktop = h("div", { class: "d-none d-xl-flex" }, m.funcionalidades.map(function (l) {
          return h("a", { class: botaoRedondo, href: l.href, "aria-label": l.texto }, icone(l.icone));
        }));
        var itensCelular = m.funcionalidades.map(function (l) {
          return h("li", {}, h("a", { class: "dropdown-item", href: l.href }, [icone(l.icone, "me-2"), l.texto]));
        });
        if (cookies) {
          // abre as configurações do <dsgovbr-cookiebar> (dsgovbr-bootstraped-cookies.js)
          var rotuloCookies = "Configurações de cookies";
          desktop.append(
            h("button", { class: botaoRedondo, type: "button", "data-dsgovbr-cookies-abrir": true, "aria-label": rotuloCookies, title: rotuloCookies }, icone("fas fa-cookie-bite"))
          );
          itensCelular.push(
            h("li", {}, h("button", { class: "dropdown-item", type: "button", "data-dsgovbr-cookies-abrir": true }, [icone("fas fa-cookie-bite", "me-2"), rotuloCookies]))
          );
        }
        if (modo) {
          var rotuloModo = "Modo escuro";
          var bd = botaoModo(botaoRedondo, { "aria-label": rotuloModo, title: rotuloModo });
          bd.append(icone("fas fa-adjust"));
          desktop.append(bd);
          var bc = botaoModo("dropdown-item");
          bc.append(icone("fas fa-adjust", "me-2"), rotuloModo);
          itensCelular.push(h("li", {}, bc));
        }
        acoesTopo.append(desktop, dropdown("Abrir funcionalidades do sistema", "fas fa-th", "Funcionalidades do sistema", itensCelular, "d-xl-none"));
      }

      if (busca) {
        acoesTopo.append(
          h(
            "button",
            { class: "btn btn-link rounded-circle d-lg-none", type: "button", "data-bs-toggle": "collapse", "data-bs-target": "#" + idBusca, "aria-expanded": "false", "aria-controls": idBusca, "aria-label": "Abrir busca" },
            icone("fas fa-search")
          )
        );
      }

      if (usuario) {
        acoesTopo.append(
          h("div", { class: "dropdown ms-1" }, [
            h("button", { class: "btn btn-light btn-sm dropdown-toggle", type: "button", "data-bs-toggle": "dropdown", "aria-expanded": "false" }, [
              icone("fas fa-user"),
              h("span", { class: "d-none d-sm-inline" }, usuario),
              h("span", { class: "visually-hidden d-sm-none" }, usuario),
            ]),
            h(
              "ul",
              { class: "dropdown-menu dropdown-menu-end" },
              m.usuario.map(function (l) {
                return h("li", {}, l ? h("a", { class: "dropdown-item", href: l.href }, l.texto) : h("hr", { class: "dropdown-divider" }));
              })
            ),
          ])
        );
      }
      cima.append(acoesTopo);

      var linhas = [cima];
      var barraPagina = null; // breadcrumb, título e ações: fora do <header>

      if (menu || titulo || subtitulo || busca) {
        var meio = h("div", { class: "d-flex flex-wrap align-items-start gap-3 mt-2" });
        if (menu) {
          meio.append(
            h(
              "button",
              { class: botaoRedondo + " mt-1", type: "button", "data-bs-toggle": "offcanvas", "data-bs-target": "#" + menu, "aria-controls": menu, "aria-label": "Abrir menu" },
              icone("fas fa-bars")
            )
          );
        }
        meio.append(
          h("div", { class: "me-auto" }, [
            titulo ? h("a", { class: "navbar-brand p-0 m-0", href: href }, titulo) : null,
            subtitulo ? h("span", { class: "dsgovbr-header-subtitulo navbar-text" }, subtitulo) : null,
          ])
        );
        if (busca) {
          meio.append(
            h("form", { class: "collapse d-lg-block col-12 col-lg-5 col-xl-4", id: idBusca, role: "search" }, [
              h("label", { class: "visually-hidden", for: idBusca + "-campo" }, "Texto da pesquisa"),
              h("input", { class: "form-control", id: idBusca + "-campo", type: "search", placeholder: "O que você procura?" }),
              h("button", { class: botaoRedondo, type: "submit", "aria-label": "Pesquisar" }, icone("fas fa-search")),
            ])
          );
        }
        linhas.push(meio);
      }

      if (pagina || m.breadcrumb.length || m.acoes.length) {
        m.breadcrumb.forEach(function (el) {
          el.setAttribute("compacto", "");
        });
        barraPagina = h("div", { class: "bg-body" }, h("div", { class: "container-lg py-2" }, [].concat(
          m.breadcrumb,
          h("div", { class: "d-flex flex-wrap gap-3 align-items-center justify-content-between" }, [
            pagina ? h("h1", { class: "h3 m-0" }, pagina) : null,
          ].concat(m.acoes))
        )));
      }

      // O <header> (com a sombra do GOV.BR DS) termina depois da busca; a barra da
      // página vem logo abaixo e as duas grudam juntas no topo (.sticky-top). A
      // sombra do header fica por cima da barra (z-1).
      this.replaceChildren(
        h("div", { class: this.hasAttribute("estatico") ? "" : "sticky-top" }, [
          h("header", { class: "navbar bg-body position-relative z-1" }, h("div", { class: "container-lg d-block" }, linhas)),
          barraPagina,
        ])
      );
      this.ouvirRolagem();
    }
  }

  // ----------------------------------------------------------------- paginação
  // <dsgovbr-paginacao total="100" por-pagina="10" pagina="1"
  //                    opcoes-por-pagina="10,25,50" informacao compacta
  //                    href="?pagina={pagina}" janela="5" rotulo="Paginação de resultados">
  //
  // Padrão: lista numerada (.pagination) com Anterior/Próxima e reticências.
  // `compacta`: "Exibir N", "1-10 de 100 itens", "Página N" (select) e setas, como o
  // rodapé da tabela do GOV.BR DS. `total` é o número de itens; sem ele, use
  // `total-paginas`. Com `href` ({pagina} vira o número) os botões são links reais
  // (servidor); sem ele, são botões. Toda troca dispara `dsgovbr:pagina` no
  // elemento (bubbles): detail { pagina, porPagina, total, totalPaginas, origem }.
  // `pagina` e `por-pagina` são atributos (e propriedades) que o componente mantém em dia.

  // Páginas a mostrar: sempre a primeira e a última, `tamanho` páginas em volta da
  // atual e "…" onde faltam várias (se falta uma só, mostra a página).
  function janelaPaginas(atual, total, tamanho) {
    var n = Math.max(3, Math.floor(tamanho) || 5);
    atual = Math.min(Math.max(1, Math.floor(atual) || 1), Math.max(1, total));
    var saida = [];
    function faixa(de, ate) {
      for (var i = de; i <= ate; i++) {
        saida.push(i);
      }
    }
    if (total <= n + 2) {
      faixa(1, total);
      return saida;
    }
    var inicio = Math.max(1, Math.min(atual - Math.floor(n / 2), total - n + 1));
    var fim = Math.min(total, inicio + n - 1);
    if (inicio > 1) {
      saida.push(1);
      if (inicio === 3) {
        saida.push(2);
      } else if (inicio > 3) {
        saida.push("…");
      }
    }
    faixa(inicio, fim);
    if (fim < total) {
      if (fim === total - 2) {
        saida.push(total - 1);
      } else if (fim < total - 2) {
        saida.push("…");
      }
      saida.push(total);
    }
    return saida;
  }

  window.dsgovbrPaginacao = { janela: janelaPaginas };

  function inteiro(valor, padrao) {
    var n = parseInt(valor, 10);
    return isNaN(n) ? padrao : n;
  }

  class Paginacao extends Base {
    static get observedAttributes() {
      return ["total", "total-paginas", "pagina", "por-pagina", "opcoes-por-pagina", "informacao", "compacta", "href", "janela", "rotulo"];
    }

    ler() {
      return null; // sem filhos: tudo vem dos atributos
    }

    get pagina() {
      return this.estado().pagina;
    }

    set pagina(valor) {
      this.ir(inteiro(valor, 1), "api");
    }

    get porPagina() {
      return this.estado().porPagina;
    }

    // Estado a partir dos atributos, já normalizado (página dentro de 1..totalPaginas).
    estado() {
      var opcoes = this.attr("opcoes-por-pagina", "").split(",").map(function (v) { return inteiro(v.trim(), 0); }).filter(function (v) { return v > 0; });
      var porPagina = Math.max(1, inteiro(this.attr("por-pagina", ""), opcoes[0] || 10));
      var total = Math.max(0, inteiro(this.attr("total", ""), 0));
      var temTotal = this.hasAttribute("total");
      var totalPaginas = temTotal ? Math.max(1, Math.ceil(total / porPagina)) : Math.max(1, inteiro(this.attr("total-paginas", ""), 1));
      var pagina = Math.min(Math.max(1, inteiro(this.attr("pagina", ""), 1)), totalPaginas);
      return { opcoes: opcoes, porPagina: porPagina, total: total, temTotal: temTotal, totalPaginas: totalPaginas, pagina: pagina };
    }

    // Vai para a página (ou muda os itens por página): atualiza os atributos, remonta e avisa.
    ir(pagina, origem, porPagina) {
      var e = this.estado();
      var novaPorPagina = porPagina || e.porPagina;
      var temTotal = e.temTotal;
      var totalPaginas = temTotal ? Math.max(1, Math.ceil(e.total / novaPorPagina)) : e.totalPaginas;
      var nova = Math.min(Math.max(1, pagina), totalPaginas);
      if (nova === e.pagina && novaPorPagina === e.porPagina) {
        return;
      }
      this._foco = this.contains(document.activeElement) ? document.activeElement.getAttribute("data-foco") : null;
      this._quieto = true; // monta uma vez só, depois dos dois atributos
      if (novaPorPagina !== e.porPagina) {
        this.setAttribute("por-pagina", String(novaPorPagina));
      }
      this.setAttribute("pagina", String(nova));
      this._quieto = false;
      this.montar();
      this.avisar(origem);
    }

    attributeChangedCallback(nome, antigo, novo) {
      if (!this._quieto) {
        super.attributeChangedCallback(nome, antigo, novo);
      }
    }

    avisar(origem) {
      var e = this.estado();
      this.dispatchEvent(new CustomEvent("dsgovbr:pagina", {
        bubbles: true,
        detail: { pagina: e.pagina, porPagina: e.porPagina, total: e.temTotal ? e.total : null, totalPaginas: e.totalPaginas, origem: origem },
      }));
    }

    montar() {
      var self = this;
      var e = this.estado();
      var compacta = this.hasAttribute("compacta");
      var id = this._uid || (this._uid = proximoId("paginacao"));
      var modelo = this.attr("href", "");

      function alvo(pagina) {
        return modelo ? modelo.replace("{pagina}", String(pagina)) : null;
      }

      function controle(rotulo, pagina, desabilitado, foco, classe, conteudo) {
        if (desabilitado) {
          // lista: o desabilitado é o .page-item.disabled (do <li>) e o texto já nomeia o controle;
          // botão de ícone: <button disabled> nativo, com o nome em aria-label
          if (classe.indexOf("btn") === 0) {
            return h("button", { type: "button", class: classe, disabled: true, "aria-label": rotulo }, conteudo);
          }
          return h("span", { class: classe, "aria-disabled": "true" }, conteudo);
        }
        var url = alvo(pagina);
        var el = h(url ? "a" : "button", { class: classe, href: url, type: url ? false : "button", "aria-label": rotulo, "data-foco": foco }, conteudo);
        el.addEventListener("click", function () { self.ir(pagina, "pagina"); });
        return el;
      }

      function seletor(rotulo, idCampo, opcoes, atual, aoMudar, foco) {
        var sel = h("select", { class: "form-select form-select-sm w-auto", id: idCampo, "data-foco": foco },
          opcoes.map(function (o) { return h("option", { value: String(o.valor), selected: o.valor === atual }, o.texto); }));
        sel.addEventListener("change", function () { aoMudar(parseInt(sel.value, 10)); });
        return h("div", { class: "d-flex align-items-center gap-2" }, [h("label", { class: "small", for: idCampo }, rotulo), sel]);
      }

      var partes = [];

      if (e.opcoes.length) {
        var opcoes = e.opcoes.indexOf(e.porPagina) === -1 ? e.opcoes.concat(e.porPagina) : e.opcoes;
        partes.push(seletor("Exibir", id + "-por-pagina", opcoes.map(function (v) { return { valor: v, texto: String(v) }; }), e.porPagina,
          function (v) { self.ir(1, "por-pagina", v); }, "por-pagina"));
      }

      if ((compacta || this.hasAttribute("informacao")) && e.temTotal) {
        var de = e.total ? (e.pagina - 1) * e.porPagina + 1 : 0;
        var ate = Math.min(e.pagina * e.porPagina, e.total);
        partes.push(h("span", { class: "small" }, e.total ? de + "-" + ate + " de " + e.total + " itens" : "0 itens"));
      }

      if (compacta) {
        var paginas = [];
        for (var i = 1; i <= e.totalPaginas; i++) {
          paginas.push({ valor: i, texto: String(i) });
        }
        var direita = h("div", { class: "d-flex align-items-center gap-2 ms-auto" }, [
          seletor("Página", id + "-pagina", paginas, e.pagina, function (v) { self.ir(v, "pagina"); }, "pagina"),
          h("div", { class: "vr" }),
          controle("Página anterior", e.pagina - 1, e.pagina <= 1, "anterior", "btn btn-link btn-sm rounded-circle", icone("fas fa-angle-left")),
          controle("Próxima página", e.pagina + 1, e.pagina >= e.totalPaginas, "proxima", "btn btn-link btn-sm rounded-circle", icone("fas fa-angle-right")),
        ]);
        partes.push(direita);
      } else {
        var itens = [];
        function item(conteudo, classe, atributos) {
          return h("li", Object.assign({ class: "page-item" + (classe ? " " + classe : "") }, atributos || {}), conteudo);
        }
        itens.push(item(controle("Página anterior", e.pagina - 1, e.pagina <= 1, "anterior", "page-link", "Anterior"), e.pagina <= 1 ? "disabled" : ""));
        janelaPaginas(e.pagina, e.totalPaginas, inteiro(this.attr("janela", ""), 5)).forEach(function (p) {
          if (p === "…") {
            itens.push(item(h("span", { class: "page-link" }, "…"), "disabled", { "aria-hidden": "true" }));
          } else if (p === e.pagina) {
            itens.push(item(h("span", { class: "page-link", "aria-label": "Página " + p }, String(p)), "active", { "aria-current": "page" }));
          } else {
            itens.push(item(controle("Página " + p, p, false, "p-" + p, "page-link", String(p))));
          }
        });
        itens.push(item(controle("Próxima página", e.pagina + 1, e.pagina >= e.totalPaginas, "proxima", "page-link", "Próxima"), e.pagina >= e.totalPaginas ? "disabled" : ""));
        partes.push(h("ul", { class: "pagination mb-0" }, itens));
      }

      var foco = this._foco;
      this._foco = null;
      this.replaceChildren(h("nav", { class: "d-flex flex-wrap align-items-center justify-content-between gap-3", "aria-label": this.attr("rotulo", "Paginação de resultados") }, partes));

      if (foco) { // o elemento focado foi recriado: devolve o foco ao equivalente
        var igual = this.querySelector('[data-foco="' + foco + '"]');
        var proximo = this.querySelector('[data-foco="proxima"]') || this.querySelector('[data-foco="anterior"]');
        var alvoFoco = igual || proximo;
        if (alvoFoco) {
          alvoFoco.focus();
        }
      }
    }
  }

  // --------------------------------------------------------------------- modal
  // O próprio elemento é o .modal.fade (como o <dsgovbr-menu> é o offcanvas): o `id`
  // dele é o alvo de `data-bs-toggle="modal"` e de `data-dsgovbr-modal-abrir="#id"`.
  //
  // <dsgovbr-modal id="confirmar" titulo="Confirmar envio" tamanho="lg" rolagem centralizado estatico>
  //   Depois de enviada, a solicitação não poderá ser alterada.   (conteúdo livre = corpo)
  //   <dsgovbr-acoes>                                             (rodapé; HTML livre)
  //     <button class="btn btn-outline-primary" data-bs-dismiss="modal">Cancelar</button>
  //     <button class="btn btn-primary" data-bs-dismiss="modal">Enviar</button>
  //   </dsgovbr-acoes>
  // </dsgovbr-modal>
  //
  // Reusa o plugin Modal do Bootstrap (foco, Escape, backdrop, retorno ao acionador):
  // exige o bootstrap.bundle. `tamanho`: sm, lg, xl ou tela-cheia. `estatico`: não fecha
  // com Escape nem clicando fora. API: abrir(), fechar(), alternar() e `aberto`.
  // Avisa com `dsgovbr:modal` (bubbles; detail { aberto }) ao abrir e ao fechar.
  var TAMANHOS_MODAL = { sm: "modal-sm", lg: "modal-lg", xl: "modal-xl", "tela-cheia": "modal-fullscreen" };

  function instanciaModal(el) {
    var bs = window.bootstrap;
    if (!bs || !bs.Modal) {
      throw new Error("dsgovbr-modal: carregue o bootstrap.bundle para abrir o modal");
    }
    return bs.Modal.getOrCreateInstance(el);
  }

  class ModalDialogo extends Base {
    static get observedAttributes() {
      return ["titulo", "tamanho", "rolagem", "centralizado", "estatico", "rotulo-fechar"];
    }

    ler() {
      return {
        acoes: nosDe(this, "dsgovbr-acoes"),
        corpo: Array.prototype.filter.call(this.childNodes, function (no) {
          return !(no.nodeType === 1 && no.localName === "dsgovbr-acoes");
        }),
      };
    }

    get aberto() {
      return this.classList.contains("show");
    }

    // O plugin só devolve o foco ao acionador quando aberto por data-bs-toggle; por API
    // (e por data-dsgovbr-modal-abrir) quem devolve é o componente.
    abrir() {
      var origem = document.activeElement;
      var instancia = instanciaModal(this);
      if (!this.aberto && origem && origem !== document.body && !this.contains(origem)) {
        this.addEventListener("hidden.bs.modal", function () {
          if (origem.isConnected && origem.offsetParent !== null) {
            origem.focus();
          }
        }, { once: true });
      }
      instancia.show();
    }

    fechar() {
      instanciaModal(this).hide();
    }

    alternar() {
      if (this.aberto) {
        this.fechar();
      } else {
        this.abrir();
      }
    }

    montar() {
      var self = this;
      var id = this.id || (this.id = proximoId("modal"));
      var idTitulo = id + "-titulo";
      var m = this._modelo;
      this.classList.add("modal", "fade");
      this.setAttribute("tabindex", "-1");
      this.setAttribute("aria-labelledby", idTitulo);
      if (this.hasAttribute("estatico")) {
        this.setAttribute("data-bs-backdrop", "static");
        this.setAttribute("data-bs-keyboard", "false");
      } else {
        this.removeAttribute("data-bs-backdrop");
        this.removeAttribute("data-bs-keyboard");
      }

      var dialogo = "modal-dialog" + (TAMANHOS_MODAL[this.attr("tamanho", "")] ? " " + TAMANHOS_MODAL[this.attr("tamanho", "")] : "") +
        (this.hasAttribute("rolagem") ? " modal-dialog-scrollable" : "") + (this.hasAttribute("centralizado") ? " modal-dialog-centered" : "");

      var conteudo = [
        h("div", { class: "modal-header" }, [
          h("h2", { class: "modal-title", id: idTitulo }, this.attr("titulo", "")),
          h("button", { type: "button", class: "btn-close", "data-bs-dismiss": "modal", "aria-label": this.attr("rotulo-fechar", "Fechar") }),
        ]),
        h("div", { class: "modal-body" }, m.corpo),
      ];
      if (m.acoes.length) {
        conteudo.push(h("div", { class: "modal-footer" }, m.acoes));
      }
      this.replaceChildren(h("div", { class: dialogo }, h("div", { class: "modal-content" }, conteudo)));

      if (!this._ouvintesModal) { // o host (.modal) é quem recebe os eventos do plugin; não muda ao remontar
        this._ouvintesModal = true;
        ["shown", "hidden"].forEach(function (nome) {
          self.addEventListener(nome + ".bs.modal", function (evento) {
            if (evento.target === self) {
              self.dispatchEvent(new CustomEvent("dsgovbr:modal", { bubbles: true, detail: { aberto: nome === "shown" } }));
            }
          });
        });
      }
    }
  }

  // Acionador sem JS próprio: <button data-dsgovbr-modal-abrir="#id">.
  document.addEventListener("click", function (evento) {
    var gatilho = evento.target && evento.target.closest ? evento.target.closest("[data-dsgovbr-modal-abrir]") : null;
    if (!gatilho) {
      return;
    }
    evento.preventDefault();
    var alvo = document.querySelector(gatilho.getAttribute("data-dsgovbr-modal-abrir"));
    if (alvo && typeof alvo.abrir === "function") {
      alvo.abrir();
    } else {
      console.error("data-dsgovbr-modal-abrir: não há <dsgovbr-modal> em", gatilho.getAttribute("data-dsgovbr-modal-abrir"));
    }
  });

  // --------------------------------------------------------------------- campo
  // <dsgovbr-campo tipo="email" nome="email" rotulo="E-mail" obrigatorio valor=""
  //                placeholder="" tamanho="sm|lg" prefixo="@" sufixo=".gov.br"
  //                ajuda="Texto de ajuda" erro="Informe um e-mail válido" sucesso="">
  //   <dsgovbr-ajuda>Texto de ajuda</dsgovbr-ajuda>   (também aceito; o atributo vence)
  //   <dsgovbr-erro>…</dsgovbr-erro>  <dsgovbr-sucesso>…</dsgovbr-sucesso>
  //   <dsgovbr-opcao valor="a" selecionada desabilitada>Texto</dsgovbr-opcao>  (select e radio)
  // </dsgovbr-campo>
  //
  // Gera rótulo + CONTROLE NATIVO (<input>, <select> ou <textarea>) + ajuda + feedback,
  // com `for`/`id`/`aria-describedby`/`aria-invalid` ligados sozinhos, só com classes do
  // Bootstrap (.form-label, .form-control, .form-select, .form-check, .form-switch,
  // .form-text, .invalid-feedback, .valid-feedback, .input-group). Como o controle é real
  // e fica dentro do <form>, o valor é enviado normalmente e os eventos input/change e a
  // validação nativa (`required`, `pattern`...) funcionam sem nada a mais.
  //
  // `tipo`: text (padrão), email, password, number, search, tel, url, date, textarea,
  // select, checkbox, switch ou radio (grupo, com <dsgovbr-opcao>). `erro` / `sucesso`
  // vazios limpam o estado. Também: `desabilitado`, `somente-leitura`, `autocomplete`,
  // `linhas` (textarea), `marcado` (checkbox/switch) e, repassados ao controle, `min`,
  // `max`, `step`, `pattern`, `maxlength`, `minlength` e `inputmode`.
  // API: `controle` (elemento nativo ou, no radio, o primeiro), `valor` (get/set) e
  // `validar()` (checkValidity + marca o campo com a mensagem nativa).
  var REPASSADOS = ["min", "max", "step", "pattern", "maxlength", "minlength", "inputmode"];
  var TIPOS_CAMPO = ["text", "email", "password", "number", "search", "tel", "url", "date", "time", "datetime-local", "month", "week", "color", "file"];

  class Campo extends Base {
    static get observedAttributes() {
      return ["tipo", "nome", "rotulo", "valor", "placeholder", "obrigatorio", "desabilitado", "somente-leitura", "tamanho",
        "autocomplete", "linhas", "ajuda", "erro", "sucesso", "prefixo", "sufixo", "marcado"].concat(REPASSADOS);
    }

    ler() {
      var self = this;
      var primeiro = function (tag) {
        var el = filhos(self, tag)[0];
        return el ? texto(el) : "";
      };
      return {
        ajuda: primeiro("dsgovbr-ajuda"),
        erro: primeiro("dsgovbr-erro"),
        sucesso: primeiro("dsgovbr-sucesso"),
        opcoes: filhos(this, "dsgovbr-opcao").map(function (o) {
          return { valor: o.getAttribute("valor") !== null ? o.getAttribute("valor") : texto(o), texto: texto(o), selecionada: o.hasAttribute("selecionada"), desabilitada: o.hasAttribute("desabilitada") };
        }),
      };
    }

    attributeChangedCallback(nome, antigo, novo) {
      if (nome === "valor" || nome === "marcado" || nome === "tipo") {
        this._descartar = true; // o autor mudou o valor: não restaura o digitado
      }
      super.attributeChangedCallback(nome, antigo, novo);
    }

    get controle() {
      return this.querySelector("input, select, textarea");
    }

    get valor() {
      var c = this.controle;
      if (!c) {
        return "";
      }
      if (this.attr("tipo", "text") === "radio") {
        var marcado = this.querySelector("input:checked");
        return marcado ? marcado.value : "";
      }
      return c.type === "checkbox" ? (c.checked ? c.value : "") : c.value;
    }

    set valor(v) {
      var c = this.controle;
      if (!c) {
        return;
      }
      if (this.attr("tipo", "text") === "radio") {
        Array.prototype.forEach.call(this.querySelectorAll("input"), function (r) { r.checked = r.value === String(v); });
      } else if (c.type === "checkbox") {
        c.checked = Boolean(v);
      } else {
        c.value = v;
      }
    }

    // Valida pelo navegador e mostra a mensagem nativa como erro do campo.
    validar() {
      var c = this.controle;
      if (!c || c.checkValidity()) {
        this.setAttribute("erro", "");
        return true;
      }
      this.setAttribute("erro", c.validationMessage);
      return false;
    }

    montar() {
      var self = this;
      var m = this._modelo;
      var id = this._uid || (this._uid = proximoId("campo"));
      var idControle = id + "-controle";
      var tipo = this.attr("tipo", "text");
      var tamanho = this.attr("tamanho", "");
      var rotulo = this.attr("rotulo", "");
      var obrigatorio = this.hasAttribute("obrigatorio");
      var ajuda = this.hasAttribute("ajuda") ? this.getAttribute("ajuda") : m.ajuda;
      var erro = this.hasAttribute("erro") ? this.getAttribute("erro") : m.erro;
      var sucesso = !erro && (this.hasAttribute("sucesso") ? this.getAttribute("sucesso") : m.sucesso);
      var idAjuda = ajuda ? id + "-ajuda" : null;
      var idFeedback = erro || sucesso ? id + "-feedback" : null;
      var descreve = [idAjuda, idFeedback].filter(Boolean).join(" ") || false;

      // Guarda o que a pessoa digitou/escolheu e o foco: remontar (ex.: erro novo) não pode apagá-los.
      var anterior = null;
      if (!this._descartar && this._montadoControle) {
        anterior = { valor: this.valor, marcado: this.controle && this.controle.type === "checkbox" ? this.controle.checked : null };
      }
      this._descartar = false;
      var tinhaFoco = this.contains(document.activeElement) ? document.activeElement.getAttribute("data-campo") : null;

      var estadoClasse = erro ? " is-invalid" : sucesso ? " is-valid" : "";
      function comuns(extra) {
        var a = {
          id: idControle, name: self.attr("nome", "") || false, required: obrigatorio, disabled: self.hasAttribute("desabilitado"),
          "aria-describedby": descreve, "aria-invalid": erro ? "true" : false, "data-campo": "controle",
        };
        REPASSADOS.forEach(function (n) { if (self.hasAttribute(n)) { a[n] = self.getAttribute(n); } });
        return Object.assign(a, extra);
      }

      var corpo = [];
      var feedback = function () {
        return [
          ajuda ? h("div", { class: "form-text", id: idAjuda }, ajuda) : null,
          erro ? h("div", { class: "invalid-feedback d-block", id: idFeedback }, erro) : null,
          sucesso ? h("div", { class: "valid-feedback d-block", id: idFeedback }, sucesso) : null,
        ];
      };

      if (tipo === "checkbox" || tipo === "switch") {
        var caixa = h("input", comuns({
          class: "form-check-input" + estadoClasse, type: "checkbox", value: this.attr("valor", "on"),
          role: tipo === "switch" ? "switch" : false, checked: this.hasAttribute("marcado"),
        }));
        corpo.push(h("div", { class: "form-check" + (tipo === "switch" ? " form-switch" : "") }, [
          caixa,
          h("label", { class: "form-check-label", for: idControle }, rotulo),
        ]));
        corpo = corpo.concat(feedback());
      } else if (tipo === "radio") {
        var grupo = h("fieldset", { "aria-describedby": descreve });
        grupo.append(h("legend", { class: "form-label fs-6" }, [rotulo, obrigatorio ? h("span", { "aria-hidden": "true" }, " *") : null]));
        m.opcoes.forEach(function (o, i) {
          var idOpcao = idControle + "-" + (i + 1);
          grupo.append(h("div", { class: "form-check" }, [
            h("input", { class: "form-check-input" + estadoClasse, type: "radio", id: i === 0 ? idControle : idOpcao, name: self.attr("nome", id), value: o.valor,
              checked: self.hasAttribute("valor") ? self.getAttribute("valor") === o.valor : o.selecionada, disabled: o.desabilitada || self.hasAttribute("desabilitado"),
              required: obrigatorio, "aria-invalid": erro ? "true" : false, "data-campo": i === 0 ? "controle" : false }),
            h("label", { class: "form-check-label", for: i === 0 ? idControle : idOpcao }, o.texto),
          ]));
        });
        corpo.push(grupo);
        corpo = corpo.concat(feedback());
      } else {
        var controle;
        var classeTam = tamanho === "sm" || tamanho === "lg" ? tamanho : "";
        if (tipo === "select") {
          controle = h("select", comuns({ class: "form-select" + (classeTam ? " form-select-" + classeTam : "") + estadoClasse }),
            m.opcoes.map(function (o) {
              return h("option", { value: o.valor, selected: self.hasAttribute("valor") ? self.getAttribute("valor") === o.valor : o.selecionada, disabled: o.desabilitada }, o.texto);
            }));
        } else if (tipo === "textarea") {
          controle = h("textarea", comuns({
            class: "form-control" + (classeTam ? " form-control-" + classeTam : "") + estadoClasse, rows: this.attr("linhas", "3"),
            placeholder: this.attr("placeholder", "") || false, readonly: this.hasAttribute("somente-leitura"), autocomplete: this.attr("autocomplete", "") || false,
          }), this.attr("valor", ""));
        } else {
          controle = h("input", comuns({
            class: "form-control" + (classeTam ? " form-control-" + classeTam : "") + estadoClasse, type: TIPOS_CAMPO.indexOf(tipo) !== -1 ? tipo : "text",
            value: this.hasAttribute("valor") ? this.getAttribute("valor") : false, placeholder: this.attr("placeholder", "") || false,
            readonly: this.hasAttribute("somente-leitura"), autocomplete: this.attr("autocomplete", "") || false,
          }));
        }
        var prefixo = this.attr("prefixo", "");
        var sufixo = this.attr("sufixo", "");
        corpo.push(h("label", { class: "form-label", for: idControle }, [rotulo, obrigatorio ? h("span", { "aria-hidden": "true" }, " *") : null]));
        corpo.push(prefixo || sufixo
          ? h("div", { class: "input-group" + (classeTam ? " input-group-" + classeTam : "") }, [
              prefixo ? h("span", { class: "input-group-text" }, prefixo) : null, controle, sufixo ? h("span", { class: "input-group-text" }, sufixo) : null,
            ])
          : controle);
        corpo = corpo.concat(feedback());
      }

      this.replaceChildren(h("div", { class: "mb-3" }, corpo));
      this._montadoControle = true;

      // Restaura o que a pessoa já tinha feito no campo e devolve o foco.
      if (anterior) {
        var c = this.controle;
        if (tipo === "radio") {
          Array.prototype.forEach.call(this.querySelectorAll("input"), function (r) { r.checked = r.value === anterior.valor; });
        } else if (c && c.type === "checkbox" && anterior.marcado !== null) {
          c.checked = anterior.marcado;
        } else if (c && c.type !== "file") {
          c.value = anterior.valor;
        }
      }
      if (tinhaFoco) {
        var alvo = this.controle;
        if (alvo) {
          alvo.focus();
        }
      }
    }
  }

  // -------------------------------------------------------------------- tabela
  // <dsgovbr-tabela titulo="Selecione usuário para modificar" busca filtros ferramentas
  //                 selecionavel total="42" por-pagina="10" opcoes-por-pagina="10,25,50"
  //                 acao="/usuarios/" densidade="media" vazio="Nenhum usuário.">
  //   <table> … </table>                          (a tabela de verdade: thead, tbody, <tr data-valor="id">)
  //   <dsgovbr-filtro nome="ativo" rotulo="Ativo">
  //     <dsgovbr-opcao valor="1">Sim</dsgovbr-opcao> <dsgovbr-opcao valor="0">Não</dsgovbr-opcao>
  //   </dsgovbr-filtro>
  //   <dsgovbr-lote-acao acao="excluir" icone="fas fa-trash">Excluir</dsgovbr-lote-acao>
  //   <dsgovbr-acoes><button class="btn btn-primary">Adicionar usuário</button></dsgovbr-acoes>
  // </dsgovbr-tabela>
  //
  // As seis partes do Table do GOV.BR DS, só com classes do Bootstrap (.table,
  // .table-responsive, .collapse, .dropdown, .btn, .btn-group, .btn-check, .form-check,
  // .input-group, .badge, .card):
  //   1. tabela     o <table> do autor é decorado (classes, coluna de seleção) e mantido;
  //   2. busca      (`busca`) lupa que abre o campo "Buscar nesta listagem" + Pesquisar;
  //   3. filtros    (<dsgovbr-filtro>) funil que abre o painel com um dropdown por filtro,
  //                 "Filtros:" com os aplicados, Filtrar e Limpar todos os filtros;
  //   4. ferramentas (`ferramentas`) três pontos: "Densidade" (Alta, Média, Baixa);
  //   5. seleção    (`selecionavel`) checkbox por linha e no cabeçalho; barra azul "N
  //                 itens selecionados" com as <dsgovbr-lote-acao>; linha com .table-active;
  //   6. paginação  (`total`/`total-paginas`) <dsgovbr-paginacao compacta> no rodapé.
  //
  // Busca e filtros ficam num <form method="get">: com `acao` o envio é nativo (renderização
  // no servidor, ex.: Django); sem `acao` não envia e só dispara os eventos. Eventos (bubbles):
  //   dsgovbr:tabela-busca / dsgovbr:tabela-filtro  detail { termo, filtros }  (cancelável)
  //   dsgovbr:tabela-selecao                        detail { quantidade, valores }
  //   dsgovbr:tabela-acao                           detail { acao, valores }
  //   dsgovbr:tabela-densidade                      detail { densidade }
  //   dsgovbr:pagina                                (do <dsgovbr-paginacao>, ver acima)
  // Não aninhe o componente dentro de outro <form> (ele tem o próprio).
  var DENSIDADES = [["alta", "Alta"], ["media", "Média"], ["baixa", "Baixa"]];

  class Tabela extends Base {
    static get observedAttributes() {
      return ["titulo", "busca", "busca-nome", "busca-valor", "busca-placeholder", "acao", "ferramentas", "selecionavel", "selecao-nome",
        "total", "total-paginas", "pagina", "por-pagina", "opcoes-por-pagina", "paginacao-href", "vazio", "carregando"];
    }

    ler() {
      var tabela = Array.prototype.find.call(this.children, function (el) { return el.localName === "table"; });
      return {
        tabela: tabela || null,
        filtros: filhos(this, "dsgovbr-filtro").map(function (f) {
          return {
            nome: f.getAttribute("nome") || "",
            rotulo: f.getAttribute("rotulo") || f.getAttribute("nome") || "",
            opcoes: filhos(f, "dsgovbr-opcao").map(function (o) {
              return { valor: o.getAttribute("valor") !== null ? o.getAttribute("valor") : texto(o), texto: texto(o), selecionada: o.hasAttribute("selecionada") };
            }),
          };
        }),
        lote: filhos(this, "dsgovbr-lote-acao").map(function (a) {
          return { acao: a.getAttribute("acao") || "", icone: a.getAttribute("icone"), texto: texto(a) };
        }),
        acoes: nosDe(this, "dsgovbr-acoes"),
      };
    }

    attributeChangedCallback(nome, antigo, novo) {
      if (!this._quieto) {
        super.attributeChangedCallback(nome, antigo, novo);
      }
    }

    get densidade() {
      var d = this.attr("densidade", "media");
      return DENSIDADES.some(function (x) { return x[0] === d; }) ? d : "media";
    }

    get valoresSelecionados() {
      return Array.prototype.map.call(this.querySelectorAll("input[data-tabela-linha]:checked"), function (c) { return c.value; });
    }

    // Busca e filtros lidos do formulário (o que seria enviado).
    consulta() {
      var form = this.querySelector("form[data-tabela-consulta]");
      var termo = form && form.elements[this.attr("busca-nome", "q")] ? form.elements[this.attr("busca-nome", "q")].value : "";
      var filtros = {};
      Array.prototype.forEach.call(this.querySelectorAll("input[data-tabela-filtro]:checked"), function (c) {
        (filtros[c.name] = filtros[c.name] || []).push(c.value);
      });
      return { termo: termo, filtros: filtros };
    }

    avisar(tipo, detalhe, cancelavel) {
      var evento = new CustomEvent("dsgovbr:tabela-" + tipo, { bubbles: true, cancelable: Boolean(cancelavel), detail: detalhe });
      this.dispatchEvent(evento);
      return evento;
    }

    // Insere (ou tira) a coluna de checkboxes na tabela do autor, sem duplicar.
    decorarSelecao(tabela, ativo) {
      var nome = this.attr("selecao-nome", "selecionados");
      var existentes = tabela.querySelectorAll("[data-dsgovbr-selecao]");
      if (!ativo) {
        Array.prototype.forEach.call(existentes, function (c) { c.remove(); });
        return;
      }
      Array.prototype.forEach.call(tabela.querySelectorAll("input[data-tabela-linha]"), function (c) { c.name = nome; });
      var cab = tabela.querySelector("thead tr");
      if (cab && !cab.querySelector("th[data-dsgovbr-selecao]")) {
        cab.insertBefore(h("th", { scope: "col", "data-dsgovbr-selecao": true },
          h("div", { class: "form-check mb-0" }, h("input", { class: "form-check-input", type: "checkbox", "aria-label": "Selecionar todas as linhas", "data-tabela-todas": true }))), cab.firstChild);
      }
      Array.prototype.forEach.call(tabela.querySelectorAll("tbody tr"), function (linha, i) {
        if (linha.querySelector("td[data-dsgovbr-selecao]")) {
          return; // já decorada (linhas novas ganham o checkbox ao remontar)
        }
        var primeira = linha.querySelector("th, td");
        var rotuloLinha = linha.getAttribute("data-rotulo") || (primeira ? texto(primeira) : "") || String(i + 1);
        linha.insertBefore(h("td", { "data-dsgovbr-selecao": true },
          h("div", { class: "form-check mb-0" }, h("input", {
            class: "form-check-input", type: "checkbox", name: nome, value: linha.getAttribute("data-valor") || String(i + 1),
            "aria-label": "Selecionar " + rotuloLinha, "data-tabela-linha": true,
          }))), linha.firstChild);
      });
    }

    // Reflete a seleção: linhas, "selecionar todas", barra e contador.
    atualizarSelecao(avisar) {
      var linhas = this.querySelectorAll("input[data-tabela-linha]");
      var marcadas = this.valoresSelecionados;
      Array.prototype.forEach.call(linhas, function (c) {
        var tr = c.closest("tr");
        if (tr) {
          tr.classList.toggle("table-active", c.checked);
        }
      });
      var todas = this.querySelector("input[data-tabela-todas]");
      if (todas) {
        todas.checked = linhas.length > 0 && marcadas.length === linhas.length;
        todas.indeterminate = marcadas.length > 0 && marcadas.length < linhas.length;
      }
      var barra = this.querySelector("[data-tabela-barra]");
      if (barra) {
        barra.hidden = marcadas.length === 0;
        barra.querySelector("[data-tabela-contador]").textContent = marcadas.length + (marcadas.length === 1 ? " item selecionado" : " itens selecionados");
      }
      if (avisar) {
        this.avisar("selecao", { quantidade: marcadas.length, valores: marcadas });
      }
    }

    aplicarDensidade() {
      var d = this.densidade;
      var raiz = this.querySelector("[data-tabela-raiz]");
      var tabela = this._modelo.tabela;
      if (raiz) {
        raiz.setAttribute("data-densidade", d);
      }
      if (tabela) {
        tabela.classList.toggle("table-sm", d === "alta");
      }
    }

    montar() {
      var self = this;
      var m = this._modelo;
      var id = this._uid || (this._uid = proximoId("tabela"));
      var idPaineis = id + "-paineis";
      var idBusca = id + "-busca";
      var idFiltros = id + "-filtros";
      var comBusca = this.hasAttribute("busca");
      var comFiltros = m.filtros.length > 0;
      var comFerramentas = this.hasAttribute("ferramentas");
      var selecionavel = this.hasAttribute("selecionavel") && Boolean(m.tabela);
      var nomeBusca = this.attr("busca-nome", "q");

      // O que a pessoa já digitou/marcou nos painéis sobrevive a uma remontagem.
      var anterior = this.querySelector("form[data-tabela-consulta]") ? this.consulta() : null;
      var tinhaFoco = this.contains(document.activeElement) ? document.activeElement.getAttribute("data-foco") : null;

      if (m.tabela) {
        m.tabela.classList.add("table", "table-hover", "align-middle");
        m.tabela.classList.add("mb-0");
        this.decorarSelecao(m.tabela, selecionavel);
      }

      function botaoFerramenta(rotulo, iconeClasses, alvo) {
        return h("button", { type: "button", class: "btn btn-link btn-sm rounded-circle", "data-bs-toggle": "collapse", "data-bs-target": "#" + alvo,
          "aria-expanded": "false", "aria-controls": alvo, "aria-label": rotulo, title: rotulo, "data-foco": alvo }, icone(iconeClasses));
      }

      // ---- barra de ferramentas: título, busca, filtros, ferramentas e ações da página
      var ferramentas = h("div", { class: "d-flex align-items-center gap-1 ms-auto" });
      if (comBusca) {
        ferramentas.append(botaoFerramenta("Buscar na listagem", "fas fa-search", idBusca));
      }
      if (comFiltros) {
        ferramentas.append(botaoFerramenta("Filtrar a listagem", "fas fa-filter", idFiltros));
      }
      if (comFerramentas) {
        var radios = DENSIDADES.map(function (d) {
          var idRadio = id + "-densidade-" + d[0];
          return [
            h("input", { type: "radio", class: "btn-check", name: id + "-densidade", id: idRadio, value: d[0], checked: self.densidade === d[0], "data-tabela-densidade": true }),
            h("label", { class: "btn btn-outline-primary btn-sm", for: idRadio }, d[1]),
          ];
        });
        ferramentas.append(h("div", { class: "dropdown" }, [
          h("button", { type: "button", class: "btn btn-link btn-sm rounded-circle", "data-bs-toggle": "dropdown", "data-bs-auto-close": "outside", "aria-expanded": "false", "aria-label": "Ferramentas da tabela", title: "Ferramentas da tabela" }, icone("fas fa-ellipsis-v")),
          h("div", { class: "dropdown-menu dropdown-menu-end p-3" }, [
            h("p", { class: "small mb-2", id: id + "-densidade-rotulo" }, "Densidade"),
            h("div", { class: "btn-group", role: "group", "aria-labelledby": id + "-densidade-rotulo" }, [].concat.apply([], radios)),
          ]),
        ]));
      }
      var cabecalho = h("div", { class: "d-flex flex-wrap align-items-center gap-2 mb-3" }, [
        this.hasAttribute("titulo") ? h("h2", { class: "h4 m-0" }, this.getAttribute("titulo")) : null,
        ferramentas,
      ].concat(m.acoes.length ? [h("div", { class: "d-flex gap-2" }, m.acoes)] : []));

      // ---- painéis de busca e de filtros (um aberto por vez), num <form method="get">
      var paineis = null;
      if (comBusca || comFiltros) {
        var corpoPaineis = h("div", { id: idPaineis });
        if (comBusca) {
          corpoPaineis.append(h("div", { class: "collapse", id: idBusca, "data-bs-parent": "#" + idPaineis },
            h("div", { class: "d-flex gap-3 mb-3" }, [
              h("input", { type: "search", class: "form-control", name: nomeBusca, value: anterior ? anterior.termo : this.attr("busca-valor", ""),
                placeholder: this.attr("busca-placeholder", "Buscar nesta listagem"), "aria-label": this.attr("busca-placeholder", "Buscar nesta listagem") }),
              h("button", { type: "submit", class: "btn btn-primary", "data-acao": "busca" }, "Pesquisar"),
            ])));
        }
        if (comFiltros) {
          var chips = h("span", { class: "d-inline-flex flex-wrap gap-1 align-items-center", "data-tabela-chips": true });
          var lista = m.filtros.map(function (f, i) {
            var idMenu = id + "-filtro-" + i;
            var marcados = anterior ? anterior.filtros[f.nome] || [] : null;
            return h("div", { class: "dropdown" }, [
              h("button", { type: "button", class: "btn btn-outline-primary btn-sm rounded-pill dropdown-toggle", "data-bs-toggle": "dropdown", "data-bs-auto-close": "outside", "aria-expanded": "false" }, f.rotulo),
              h("div", { class: "dropdown-menu p-2" }, f.opcoes.map(function (o, j) {
                var idCampo = idMenu + "-" + j;
                return h("div", { class: "form-check mx-2 my-1" }, [
                  h("input", { class: "form-check-input", type: "checkbox", id: idCampo, name: f.nome, value: o.valor,
                    checked: marcados ? marcados.indexOf(o.valor) !== -1 : o.selecionada, "data-tabela-filtro": true, "data-rotulo-filtro": f.rotulo, "data-rotulo-opcao": o.texto }),
                  h("label", { class: "form-check-label", for: idCampo }, o.texto),
                ]);
              })),
            ]);
          });
          corpoPaineis.append(h("div", { class: "collapse", id: idFiltros, "data-bs-parent": "#" + idPaineis },
            h("div", { class: "card shadow-sm mb-3" }, h("div", { class: "card-body" }, [
              h("div", { class: "d-flex flex-wrap gap-2 mb-3" }, lista),
              h("div", { class: "d-flex flex-wrap align-items-center justify-content-between gap-2" }, [
                h("div", { class: "small d-flex flex-wrap align-items-center gap-2" }, [h("span", {}, "Filtros:"), chips]),
                h("div", { class: "d-flex gap-2 ms-auto" }, [
                  h("button", { type: "submit", class: "btn btn-primary btn-sm", "data-acao": "filtro" }, "Filtrar"),
                  h("button", { type: "button", class: "btn btn-outline-primary btn-sm", "data-tabela-limpar": true }, "Limpar todos os filtros"),
                ]),
              ]),
            ]))));
        }
        paineis = h("form", { method: "get", action: this.attr("acao", "") || false, role: "search", "aria-label": "Busca e filtros da listagem", "data-tabela-consulta": true }, corpoPaineis);
      }

      // ---- barra de itens selecionados (azul) com as ações em lote
      var barra = null;
      if (selecionavel) {
        // `hidden` fica num wrapper: .d-flex (!important) venceria o [hidden] do próprio elemento
        barra = h("div", { hidden: true, "data-tabela-barra": true },
          h("div", { class: "bg-primary text-white d-flex flex-wrap align-items-center gap-3 px-3 py-2" }, [
            h("span", { class: "fw-semibold me-auto", role: "status", "aria-live": "polite", "data-tabela-contador": true }),
          ].concat(m.lote.map(function (a) {
            return h("button", { type: "button", class: "btn btn-link text-white", "data-tabela-acao": a.acao }, [icone(a.icone, "me-2"), a.texto]);
          }))));
      }

      // ---- tabela (responsiva) com estados de vazio e de carregamento
      var corpo = h("div", { class: "table-responsive" }, m.tabela ? [m.tabela] : []);
      var linhasDados = m.tabela ? m.tabela.querySelectorAll("tbody tr").length : 0;
      var estados = [];
      if (this.hasAttribute("carregando")) {
        estados.push(h("div", { class: "text-center p-4", role: "status" }, [h("span", { class: "spinner-border spinner-border-sm me-2", "aria-hidden": "true" }), "Carregando…"]));
      } else if (linhasDados === 0) {
        estados.push(h("p", { class: "text-center text-body-secondary p-4 m-0" }, this.attr("vazio", "Nenhum registro encontrado.")));
      }

      // ---- rodapé: paginação compacta
      var rodape = null;
      if (this.hasAttribute("total") || this.hasAttribute("total-paginas")) {
        var paginacao = document.createElement("dsgovbr-paginacao");
        paginacao.setAttribute("compacta", "");
        paginacao.setAttribute("rotulo", "Paginação da tabela");
        ["total", "total-paginas", "pagina", "por-pagina", "opcoes-por-pagina"].forEach(function (n) {
          if (self.hasAttribute(n)) {
            paginacao.setAttribute(n, self.getAttribute(n));
          }
        });
        if (this.hasAttribute("paginacao-href")) {
          paginacao.setAttribute("href", this.getAttribute("paginacao-href"));
        }
        rodape = h("div", { class: "mt-3" }, paginacao);
      }

      var raiz = h("div", { "data-tabela-raiz": true, "aria-busy": this.hasAttribute("carregando") ? "true" : false },
        [cabecalho, paineis, barra, corpo].concat(estados, [rodape]));
      this.replaceChildren(raiz);
      this.aplicarDensidade();
      this.atualizarSelecao(false);
      this.atualizarChips();

      if (tinhaFoco) {
        var alvo = this.querySelector('[data-foco="' + tinhaFoco + '"]');
        if (alvo) {
          alvo.focus();
        }
      }
      this.ligar();
    }

    // "Filtros:" com um chip por opção marcada.
    atualizarChips() {
      var chips = this.querySelector("[data-tabela-chips]");
      if (!chips) {
        return;
      }
      var marcados = Array.prototype.map.call(this.querySelectorAll("input[data-tabela-filtro]:checked"), function (c) {
        return h("span", { class: "badge rounded-pill text-bg-secondary" }, c.getAttribute("data-rotulo-filtro") + ": " + c.getAttribute("data-rotulo-opcao"));
      });
      chips.replaceChildren.apply(chips, marcados);
    }

    // Eventos por delegação no host: valem depois de qualquer remontagem.
    ligar() {
      if (this._ligado) {
        return;
      }
      this._ligado = true;
      var self = this;

      this.addEventListener("change", function (e) {
        var alvo = e.target;
        if (alvo.matches("input[data-tabela-todas]")) {
          Array.prototype.forEach.call(self.querySelectorAll("input[data-tabela-linha]"), function (c) { c.checked = alvo.checked; });
          self.atualizarSelecao(true);
        } else if (alvo.matches("input[data-tabela-linha]")) {
          self.atualizarSelecao(true);
        } else if (alvo.matches("input[data-tabela-filtro]")) {
          self.atualizarChips();
        } else if (alvo.matches("input[data-tabela-densidade]")) {
          self._quieto = true;
          self.setAttribute("densidade", alvo.value);
          self._quieto = false;
          self.aplicarDensidade();
          self.avisar("densidade", { densidade: alvo.value });
        }
      });

      this.addEventListener("click", function (e) {
        var lote = e.target.closest ? e.target.closest("[data-tabela-acao]") : null;
        if (lote) {
          self.avisar("acao", { acao: lote.getAttribute("data-tabela-acao"), valores: self.valoresSelecionados });
          return;
        }
        if (e.target.closest && e.target.closest("[data-tabela-limpar]")) {
          Array.prototype.forEach.call(self.querySelectorAll("input[data-tabela-filtro]"), function (c) { c.checked = false; });
          self.atualizarChips();
          var filtrar = self.querySelector('[data-acao="filtro"]');
          var form = self.querySelector("form[data-tabela-consulta]");
          if (form && form.requestSubmit) {
            form.requestSubmit(filtrar);
          }
        }
      });

      this.addEventListener("submit", function (e) {
        if (!e.target.matches || !e.target.matches("form[data-tabela-consulta]")) {
          return;
        }
        var origem = e.submitter && e.submitter.getAttribute("data-acao") ? e.submitter.getAttribute("data-acao") : "busca";
        var evento = self.avisar(origem, self.consulta(), true);
        if (evento.defaultPrevented || !self.hasAttribute("acao")) {
          e.preventDefault();
        }
      });
    }
  }

  // Elementos-dado: só carregam atributos e conteúdo para o componente pai, que os
  // troca pelo HTML final. Definidos para ficarem "upgraded" e documentados; o CSS
  // os oculta se sobrarem fora de um pai.
  [
    "dsgovbr-item", "dsgovbr-pasta", "dsgovbr-menu-rodape", "dsgovbr-coluna", "dsgovbr-rede", "dsgovbr-logo", "dsgovbr-aviso",
    "dsgovbr-acesso-rapido", "dsgovbr-funcionalidades", "dsgovbr-usuario-menu", "dsgovbr-divisor", "dsgovbr-acoes",
    "dsgovbr-ajuda", "dsgovbr-erro", "dsgovbr-sucesso", "dsgovbr-opcao", "dsgovbr-filtro", "dsgovbr-lote-acao",
  ].forEach(function (nome) {
    if (!window.customElements.get(nome)) {
      window.customElements.define(nome, class extends HTMLElement {});
    }
  });

  // Ordem importa só por clareza: o breadcrumb também funciona se for definido
  // depois do header (ele é movido e continua idempotente).
  [
    ["dsgovbr-breadcrumb", Breadcrumb],
    ["dsgovbr-menu", Menu],
    ["dsgovbr-footer", Footer],
    ["dsgovbr-header", Header],
    ["dsgovbr-paginacao", Paginacao],
    ["dsgovbr-modal", ModalDialogo],
    ["dsgovbr-campo", Campo],
    ["dsgovbr-tabela", Tabela],
  ].forEach(function (par) {
    if (!window.customElements.get(par[0])) {
      window.customElements.define(par[0], par[1]);
    }
  });
})();
