"""Menu do tema: apps do admin mais pastas e itens registrados no ``menus.py`` dos apps.

- Pasta (``register_folder``) agrupa itens; item (``register_item``) pode ter submenus em
  vários níveis (``parent`` ou ``MenuItem.add_item``).
- ``permission``: uma permissão (``str``) ou várias (lista/tupla, basta qualquer uma).
- ``check(request)``: regra livre de visibilidade.
- ``badge``: ``MenuItemBadge(label, color)``; ``label`` pode ser ``label(request)``.
- ``color``: cor do Bootstrap (``danger``, ``success``…) aplicada ao ícone.
- Pasta ou submenu sem link e sem itens visíveis some do menu.
"""

from __future__ import annotations

import logging
from collections.abc import Callable, Iterable
from typing import Any
from urllib.parse import quote

from django.urls import reverse, NoReverseMatch
from django.utils.module_loading import autodiscover_modules

from dsgovbr.icons import app_icon, default_app_icon, default_menu_icon, model_icon

Permission = str | Iterable[str] | None
Check = Callable[[Any], bool] | None

# links que não levam a lugar nenhum: pasta ou submenu só agrupador
SEM_LINK = ("", "#", "javascript:void(0);", "javascript:void(0)")
DEFAULT_ORDER = 9999

logger = logging.getLogger(__name__)


def _resolve_url(url: str | None) -> str:
    """Nome de rota (``app:view``) vira URL; caminho, URL absoluta e ``javascript:`` ficam."""
    if not url:
        return ""
    if url.startswith(("/", "http://", "https://", "javascript:", "#")):
        return url
    try:
        return reverse(url)
    except NoReverseMatch:
        return url


def _sem_link(url: str | None) -> bool:
    return (url or "") in SEM_LINK


def _url_ativa(url: str, request: Any) -> bool:
    """Mesma regra do template: o link está contido no caminho atual."""
    path = getattr(request, "path", None)
    if _sem_link(url) or not path:
        return False
    return url in quote(path, safe="/")


def _sort_key(item: dict) -> tuple:
    ordem = item.get("_order")
    return (ordem if ordem is not None else DEFAULT_ORDER, item["name"].lower())


def has_permission(user: Any, permission: Permission) -> bool:
    """Sem ``permission``: livre. ``str`` ou lista/tupla: usuário autenticado com qualquer uma."""
    if not permission:
        return True
    if user is None or not getattr(user, "is_authenticated", False):
        return False
    perms = [permission] if isinstance(permission, str) else list(permission)
    return any(user.has_perm(perm) for perm in perms)


class MenuItemBadge:
    """Selo ao lado do nome: texto fixo ou ``label(request)`` (um contador, por exemplo).

    ``color`` é uma cor do Bootstrap (``primary``, ``danger``…); ``label`` vazio ou ``None``
    esconde o selo.
    """

    def __init__(
        self, label: str | int | Callable[[Any], Any], color: str = "primary"
    ) -> None:
        self.label = label
        self.color = color or "primary"

    def to_dict(self, request: Any = None) -> dict | None:
        label = self.label(request) if callable(self.label) else self.label
        if label is None or label == "":
            return None
        return {"label": str(label), "color": self.color}


def _badge_dict(badge: MenuItemBadge | str | int | None, request: Any) -> dict | None:
    if badge is None or badge == "":
        return None
    if not isinstance(badge, MenuItemBadge):
        badge = MenuItemBadge(badge)
    try:
        return badge.to_dict(request)
    except Exception:
        logger.exception("Erro ao calcular o badge do menu")
        return None


class _Visibilidade:
    permission: Permission
    check: Check

    def is_visible(self, request: Any) -> bool:
        if self.check and not self.check(request):
            return False
        return has_permission(getattr(request, "user", None), self.permission)


class MenuItem(_Visibilidade):
    def __init__(
        self,
        name: str,
        url: str | None,
        icon: str | None = None,
        order: int | None = None,
        permission: Permission = None,
        check: Check = None,
        badge: MenuItemBadge | str | int | None = None,
        color: str | None = None,
    ) -> None:
        self.name = name
        self.url = url or ""
        self._icon = icon
        self.order = order
        self.permission = permission
        self.check = check
        self.badge = badge
        self.color = color
        self.subitems: list[MenuItem] = []

    @property
    def icon(self) -> str:
        """Ícone informado ou ``DSGOVBR_DEFAULT_MENU_ICON``."""
        return self._icon or default_menu_icon()

    @icon.setter
    def icon(self, value: str | None) -> None:
        self._icon = value

    def add_item(
        self,
        name: str,
        url: str | None = None,
        icon: str | None = None,
        order: int | None = None,
        permission: Permission = None,
        check: Check = None,
        badge: MenuItemBadge | str | int | None = None,
        color: str | None = None,
    ) -> MenuItem:
        """Submenu: item filho. Sem ``url``, o item só agrupa."""
        return _add_item(
            self.subitems, name, url, icon, order, permission, check, badge, color
        )

    def get_item(self, name: str) -> MenuItem | None:
        return _find_item(self.subitems, name)

    def to_dict(self, request: Any = None) -> dict:
        return {
            "name": self.name,
            "admin_url": _resolve_url(self.url),
            "icon": self.icon,
            "color": self.color,
            "badge": _badge_dict(self.badge, request),
            "subitems": [],
        }

    def build(self, request: Any, menu_id: str) -> dict | None:
        """Dict do item com os subitens visíveis; ``None`` se for agrupador vazio."""
        data = self.to_dict(request)
        data["menu_id"] = menu_id
        for indice, sub in enumerate(self.subitems, start=1):
            if not sub.is_visible(request):
                continue
            sub_data = sub.build(request, f"{menu_id}-{indice}")
            if sub_data is not None:
                sub_data["_order"] = sub.order
                data["subitems"].append(sub_data)
        data["subitems"].sort(key=_sort_key)
        for sub_data in data["subitems"]:
            sub_data.pop("_order", None)
        if not data["subitems"] and _sem_link(data["admin_url"]):
            return None
        # submenu já aberto quando a página atual está dentro dele
        data["open"] = any(
            _url_ativa(sub["admin_url"], request) or sub.get("open")
            for sub in data["subitems"]
        )
        return data


def _find_item(items: list[MenuItem], name: str) -> MenuItem | None:
    """Busca por nome em profundidade (submenus inclusos)."""
    for item in items:
        if item.name == name:
            return item
        achado = _find_item(item.subitems, name)
        if achado is not None:
            return achado
    return None


def _add_item(
    items: list[MenuItem],
    name: str,
    url: str | None,
    icon: str | None,
    order: int | None,
    permission: Permission,
    check: Check,
    badge: MenuItemBadge | str | int | None,
    color: str | None,
) -> MenuItem:
    # Evitar duplicados por nome/url
    for item in items:
        if item.name == name and item.url == (url or ""):
            return item
    item = MenuItem(name, url, icon, order, permission, check, badge, color)
    items.append(item)
    return item


class MenuFolder(_Visibilidade):
    def __init__(
        self,
        app_label: str,
        name: str,
        icon: str | None = None,
        app_url: str | None = None,
        order: int | None = None,
        permission: Permission = None,
        check: Check = None,
        badge: MenuItemBadge | str | int | None = None,
        color: str | None = None,
    ) -> None:
        self.app_label = app_label
        self.name = name
        self._icon = icon
        self.app_url = app_url or "javascript:void(0);"
        self.order = order
        self.permission = permission
        self.check = check
        self.badge = badge
        self.color = color
        self._items: list[MenuItem] = []

    @property
    def icon(self) -> str:
        """Ícone informado ou ``DSGOVBR_DEFAULT_APP_ICON``."""
        return self._icon or default_app_icon()

    @icon.setter
    def icon(self, value: str | None) -> None:
        self._icon = value

    def add_item(
        self,
        name: str,
        url: str | None = None,
        icon: str | None = None,
        order: int | None = None,
        permission: Permission = None,
        check: Check = None,
        badge: MenuItemBadge | str | int | None = None,
        color: str | None = None,
    ) -> MenuItem:
        return _add_item(
            self._items, name, url, icon, order, permission, check, badge, color
        )

    def get_item(self, name: str) -> MenuItem | None:
        return _find_item(self._items, name)

    def to_dict(self, request: Any = None) -> dict:
        return {
            "name": self.name,
            "app_label": self.app_label,
            "app_url": _resolve_url(self.app_url),
            "icon": self.icon,
            "color": self.color,
            "badge": _badge_dict(self.badge, request),
            "models": [],
        }


def get_full_admin_app_list(request):
    """
    Apps e models do admin que o usuário do ``request`` pode ver.

    Antes o menu usava um usuário fictício superusuário e mostrava a todo usuário
    staff os apps e models sem permissão. Agora valem as permissões reais: sem
    acesso ao admin (``AdminSite.has_permission``), a lista vem vazia (os itens registrados no
    ``menus.py`` continuam com ``permission``/``check`` próprios).
    """
    from django.contrib import admin
    from django.contrib.admin import AdminSite

    user = getattr(request, "user", None)
    if user is None or not getattr(user, "is_authenticated", False):
        return []
    try:
        # quem não entra no admin (inativo ou sem is_staff) não vê os apps do admin
        if not admin.site.has_permission(request):
            return []
        # implementação base: o DSGovBrAdminSite.get_app_list monta o menu a partir daqui (evita recursão)
        return AdminSite.get_app_list(admin.site, request)
    except Exception:
        logger.exception("Erro ao obter a lista de apps do admin")
        return []


class MenuRegistry:
    def __init__(self) -> None:
        self._folders: dict[str, MenuFolder] = {}
        self._reorder_callbacks: list[Callable[[list[dict]], list[dict] | None]] = []
        self._global_order: list[str] = []
        self._items_order: dict[str, list[str]] = {}

    def register_folder(
        self,
        app_label: str,
        name: str | None = None,
        icon: str | None = None,
        app_url: str | None = None,
        order: int | None = None,
        permission: Permission = None,
        check: Check = None,
        badge: MenuItemBadge | str | int | None = None,
        color: str | None = None,
    ) -> MenuFolder:
        if app_label not in self._folders:
            self._folders[app_label] = MenuFolder(
                app_label=app_label,
                name=name or app_label.capitalize(),
                icon=icon,
                app_url=app_url,
                order=order,
                permission=permission,
                check=check,
                badge=badge,
                color=color,
            )
        else:
            folder = self._folders[app_label]
            if name:
                folder.name = name
            if icon:
                folder.icon = icon
            if app_url:
                folder.app_url = app_url
            if order is not None:
                folder.order = order
            if permission:
                folder.permission = permission
            if check:
                folder.check = check
            if badge is not None:
                folder.badge = badge
            if color:
                folder.color = color
        return self._folders[app_label]

    def register_item(
        self,
        app_label: str,
        name: str,
        url: str | None,
        icon: str | None = None,
        order: int | None = None,
        permission: Permission = None,
        check: Check = None,
        badge: MenuItemBadge | str | int | None = None,
        color: str | None = None,
        parent: MenuItem | str | Iterable[str] | None = None,
    ) -> MenuItem:
        """Item da pasta ``app_label``; com ``parent``, vira submenu.

        ``parent``: o ``MenuItem`` pai, o nome dele ou o caminho de nomes
        (``["Utilitários", "Diagnóstico"]``). Nome ainda não registrado vira um
        agrupador sem link.
        """
        folder = self.register_folder(app_label)
        container: MenuFolder | MenuItem = folder
        if isinstance(parent, MenuItem):
            container = parent
        elif isinstance(parent, str):
            container = folder.get_item(parent) or folder.add_item(parent)
        elif parent is not None:
            for nome in parent:
                container = container.get_item(nome) or container.add_item(nome)
        return container.add_item(
            name, url, icon, order, permission, check, badge, color
        )

    def set_order(self, order_list: Iterable[str]) -> None:
        self._global_order = list(order_list)

    def set_items_order(self, app_label: str, order_list: Iterable[str]) -> None:
        self._items_order[app_label] = list(order_list)

    def add_reorder_callback(
        self, callback: Callable[[list[dict]], list[dict] | None]
    ) -> None:
        self._reorder_callbacks.append(callback)

    def get_menu_list(self, request: Any) -> list[dict]:
        # apps e models do admin com as permissões do usuário atual
        admin_app_list = get_full_admin_app_list(request)

        folders_dict: dict[str, dict] = {}

        # 1. Processar a lista vinda do Django Admin
        for app in admin_app_list:
            app_label = app.get("app_label")
            # ícone do AppConfig só para pasta nova: pasta registrada no menus.py mantém o seu
            novo = app_label not in self._folders
            reg_folder = self.register_folder(
                app_label,
                name=app.get("name"),
                icon=app_icon(app_label) if novo else None,
                app_url=app.get("app_url"),
            )

            models_list = []
            for model in app.get("models", []):
                models_list.append(
                    {
                        "name": model.get("name"),
                        "admin_url": model.get("admin_url"),
                        # model é um dict do Django: o ícone vem do ModelAdmin registrado
                        "icon": model_icon(model.get("model")),
                        "color": None,
                        "badge": None,
                        "subitems": [],
                    }
                )

            folder_data = reg_folder.to_dict(request)
            folder_data.update(
                app_url=reg_folder.app_url or app.get("app_url"),
                models=models_list,
                order=reg_folder.order,
            )
            folders_dict[app_label] = folder_data

        # 2. Mesclar com as customizações registradas no MenuRegistry
        for app_label, reg_folder in self._folders.items():
            if not reg_folder.is_visible(request):
                folders_dict.pop(app_label, None)
                continue

            if app_label not in folders_dict:
                folder_data = reg_folder.to_dict(request)
                folder_data["order"] = reg_folder.order
                folders_dict[app_label] = folder_data

            folder_data = folders_dict[app_label]
            for indice, item in enumerate(reg_folder._items, start=1):
                if not item.is_visible(request):
                    continue

                item_dict = item.build(request, f"menu-{app_label}-{indice}")
                if item_dict is None:
                    continue
                # Evitar duplicados
                if not any(
                    m["name"] == item_dict["name"]
                    and m["admin_url"] == item_dict["admin_url"]
                    for m in folder_data["models"]
                ):
                    item_dict["_order"] = item.order
                    folder_data["models"].append(item_dict)

        # 3. Remover pastas vazias que sejam apenas agrupadoras (sem link)
        active_folders = [
            folder_data
            for folder_data in folders_dict.values()
            if folder_data["models"] or not _sem_link(folder_data["app_url"])
        ]

        # pasta já aberta quando a página atual está num item dela
        for folder_data in active_folders:
            folder_data["open"] = any(
                _url_ativa(m["admin_url"], request) or m.get("open")
                for m in folder_data["models"]
            )

        # 4. Ordenar os itens dentro de cada pasta
        for folder_data in active_folders:
            app_label = folder_data["app_label"]
            models = folder_data["models"]

            if app_label in self._items_order:
                order_list = self._items_order[app_label]

                def item_sort_key(item: dict, order_list: list[str] = order_list):
                    try:
                        idx = order_list.index(item["name"])
                        return (0, idx, item["name"].lower())
                    except ValueError:
                        return (1, *_sort_key(item))

                models.sort(key=item_sort_key)
            else:
                models.sort(key=_sort_key)

            # Limpar chave de ordenação temporária
            for m in models:
                m.pop("_order", None)

        # 5. Ordenar as pastas globalmente
        def folder_key(folder: dict) -> tuple:
            ordem = folder.get("order")
            return (
                ordem if ordem is not None else DEFAULT_ORDER,
                folder["name"].lower(),
            )

        if self._global_order:

            def folder_sort_key(folder: dict) -> tuple:
                try:
                    idx = self._global_order.index(folder["app_label"])
                    return (0, idx, folder["name"].lower())
                except ValueError:
                    return (1, *folder_key(folder))

            active_folders.sort(key=folder_sort_key)
        else:
            active_folders.sort(key=folder_key)

        # 6. Aplicar os callbacks de reordenação customizados
        for callback in self._reorder_callbacks:
            try:
                res = callback(active_folders)
                if res is not None:
                    active_folders = res
            except Exception:
                logger.exception("Erro no callback de reordenação do menu")

        return active_folders


registry = MenuRegistry()


def register_folder(
    app_label: str,
    name: str | None = None,
    icon: str | None = None,
    app_url: str | None = None,
    order: int | None = None,
    permission: Permission = None,
    check: Check = None,
    badge: MenuItemBadge | str | int | None = None,
    color: str | None = None,
) -> MenuFolder:
    return registry.register_folder(
        app_label, name, icon, app_url, order, permission, check, badge, color
    )


def register_item(
    app_label: str,
    name: str,
    url: str | None,
    icon: str | None = None,
    order: int | None = None,
    permission: Permission = None,
    check: Check = None,
    badge: MenuItemBadge | str | int | None = None,
    color: str | None = None,
    parent: MenuItem | str | Iterable[str] | None = None,
) -> MenuItem:
    return registry.register_item(
        app_label, name, url, icon, order, permission, check, badge, color, parent
    )


def set_order(order_list: Iterable[str]) -> None:
    registry.set_order(order_list)


def set_items_order(app_label: str, order_list: Iterable[str]) -> None:
    registry.set_items_order(app_label, order_list)


def add_reorder_callback(callback: Callable[[list[dict]], list[dict] | None]) -> None:
    registry.add_reorder_callback(callback)


def get_menu_list(request: Any) -> list[dict]:
    return registry.get_menu_list(request)


def autodiscover() -> None:
    autodiscover_modules("menus")
