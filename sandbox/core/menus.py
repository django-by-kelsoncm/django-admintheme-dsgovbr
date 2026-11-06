import dsgovbr.menus as menus

# 1. Pasta Sistema (Início, Painel)
menus.register_folder("sistema", name="Sistema", icon="fas fa-desktop", order=0)
menus.register_item("sistema", "Início", "core:home", icon="fas fa-home", order=1)
menus.register_item(
    "sistema", "Painel", "core:dashboard", icon="fas fa-tachometer-alt", order=2
)

# 2. Pasta Extras (Formulários, Showcase, QA)
menus.register_folder("extras", name="Extras", icon="fas fa-plus-circle", order=90)
menus.register_item(
    "extras", "Formulários", "public_forms:demo", icon="fas fa-wpforms", order=1
)
menus.register_item(
    "extras",
    "Showcase UI",
    "ui_showcase:showcase",
    icon="fas fa-laptop-code",
    order=2,
)
menus.register_item(
    "extras", "QA Panel", "qa_orchestrator:panel", icon="fas fa-vial", order=3
)

# Submenu em vários níveis, badge e cor (dsgovbr 7.3.0)
menus.register_item(
    "extras",
    "Novidades",
    "ui_showcase:showcase",
    icon="fas fa-star",
    order=4,
    color="warning",
    badge=menus.MenuItemBadge("novo", "success"),
    parent="Laboratório",
)
menus.register_item(
    "extras",
    "Pendências",
    "qa_orchestrator:panel",
    icon="fas fa-tasks",
    # badge dinâmico: label(request) é chamado a cada página
    badge=menus.MenuItemBadge(lambda request: 3, "danger"),
    parent=["Laboratório", "Diagnóstico"],
)
menus.register_item(
    "extras",
    "Só para staff",
    "public_forms:demo",
    icon="fas fa-user-shield",
    # qualquer uma das permissões basta
    permission=["auth.view_user", "auth.change_user"],
    parent=["Laboratório", "Diagnóstico"],
)

# 3. Definição da ordem global dos menus
menus.set_order(
    [
        "sistema",
        "cadastro",
        "editorial",
        "atendimento",
        "eventos",
        "media_library",
        "accounts",
        "extras",
    ]
)
