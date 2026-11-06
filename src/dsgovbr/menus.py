import logging

from django.urls import reverse, NoReverseMatch
from django.utils.module_loading import autodiscover_modules

from dsgovbr.icons import app_icon, model_icon


class MenuItem:
    def __init__(self, name, url, icon=None, order=None, permission=None, check=None):
        self.name = name
        self.url = url
        self.icon = icon or "fas fa-angle-right"
        self.order = order
        self.permission = permission
        self.check = check

    def is_visible(self, request):
        if self.check and not self.check(request):
            return False
        if self.permission:
            if not request.user.is_authenticated:
                return False
            if not request.user.has_perm(self.permission):
                return False
        return True

    def to_dict(self, request=None):
        resolved_url = self.url
        if not (
            self.url.startswith("/")
            or self.url.startswith("http://")
            or self.url.startswith("https://")
            or self.url.startswith("javascript:")
        ):
            try:
                resolved_url = reverse(self.url)
            except NoReverseMatch:
                pass

        return {
            "name": self.name,
            "admin_url": resolved_url,
            "icon": self.icon,
        }


class MenuFolder:
    def __init__(
        self,
        app_label,
        name,
        icon=None,
        app_url=None,
        order=None,
        permission=None,
        check=None,
    ):
        self.app_label = app_label
        self.name = name
        self.icon = icon or "fas fa-folder"
        self.app_url = app_url or "javascript:void(0);"
        self.order = order
        self.permission = permission
        self.check = check
        self._items = []

    def add_item(self, name, url, icon=None, order=None, permission=None, check=None):
        # Evitar duplicados por nome/url
        for item in self._items:
            if item.name == name and item.url == url:
                return item
        item = MenuItem(name, url, icon, order, permission, check)
        self._items.append(item)
        return item

    def is_visible(self, request):
        if self.check and not self.check(request):
            return False
        if self.permission:
            if not request.user.is_authenticated:
                return False
            if not request.user.has_perm(self.permission):
                return False
        return True

    def to_dict(self, request=None):
        resolved_app_url = self.app_url
        if not (
            self.app_url.startswith("/")
            or self.app_url.startswith("http://")
            or self.app_url.startswith("https://")
            or self.app_url.startswith("javascript:")
        ):
            try:
                resolved_app_url = reverse(self.app_url)
            except NoReverseMatch:
                pass

        return {
            "name": self.name,
            "app_label": self.app_label,
            "app_url": resolved_app_url,
            "icon": self.icon,
            "models": [],
        }


logger = logging.getLogger(__name__)


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
    def __init__(self):
        self._folders = {}
        self._reorder_callbacks = []
        self._global_order = []
        self._items_order = {}

    def register_folder(
        self,
        app_label,
        name=None,
        icon=None,
        app_url=None,
        order=None,
        permission=None,
        check=None,
    ):
        if app_label not in self._folders:
            self._folders[app_label] = MenuFolder(
                app_label=app_label,
                name=name or app_label.capitalize(),
                icon=icon,
                app_url=app_url,
                order=order,
                permission=permission,
                check=check,
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
        return self._folders[app_label]

    def register_item(
        self,
        app_label,
        name,
        url,
        icon=None,
        order=None,
        permission=None,
        check=None,
    ):
        folder = self.register_folder(app_label)
        return folder.add_item(name, url, icon, order, permission, check)

    def set_order(self, order_list):
        self._global_order = list(order_list)

    def set_items_order(self, app_label, order_list):
        self._items_order[app_label] = list(order_list)

    def add_reorder_callback(self, callback):
        self._reorder_callbacks.append(callback)

    def get_menu_list(self, request):
        # apps e models do admin com as permissões do usuário atual
        admin_app_list = get_full_admin_app_list(request)

        folders_dict = {}

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
                    }
                )

            folders_dict[app_label] = {
                "name": reg_folder.name,
                "app_label": app_label,
                "app_url": reg_folder.app_url or app.get("app_url"),
                "icon": reg_folder.icon,
                "models": models_list,
                "order": reg_folder.order,
            }

        # 2. Mesclar com as customizações registradas no MenuRegistry
        for app_label, reg_folder in self._folders.items():
            if not reg_folder.is_visible(request):
                continue

            if app_label not in folders_dict:
                folders_dict[app_label] = {
                    "name": reg_folder.name,
                    "app_label": app_label,
                    "app_url": reg_folder.app_url,
                    "icon": reg_folder.icon,
                    "models": [],
                    "order": reg_folder.order,
                }

            folder_data = folders_dict[app_label]
            for item in reg_folder._items:
                if not item.is_visible(request):
                    continue

                item_dict = item.to_dict(request)
                # Evitar duplicados
                if not any(
                    m["name"] == item_dict["name"]
                    and m["admin_url"] == item_dict["admin_url"]
                    for m in folder_data["models"]
                ):
                    item_dict["_order"] = item.order
                    folder_data["models"].append(item_dict)

        # 3. Remover pastas vazias que sejam apenas agrupadoras (javascript:void(0))
        active_folders = []
        for app_label, folder_data in folders_dict.items():
            is_dropdown = (
                folder_data["app_url"] == "javascript:void(0);"
                or not folder_data["app_url"]
            )
            if is_dropdown and len(folder_data["models"]) == 0:
                continue
            active_folders.append(folder_data)

        # 4. Ordenar os itens dentro de cada pasta
        for folder_data in active_folders:
            app_label = folder_data["app_label"]
            models = folder_data["models"]

            if app_label in self._items_order:
                order_list = self._items_order[app_label]

                def item_sort_key(item):
                    try:
                        idx = order_list.index(item["name"])
                        return (0, idx, item["name"].lower())
                    except ValueError:
                        custom_ord = item.get("_order")
                        return (
                            1,
                            custom_ord if custom_ord is not None else 9999,
                            item["name"].lower(),
                        )

                models.sort(key=item_sort_key)
            else:
                models.sort(
                    key=lambda x: (
                        x.get("_order") if x.get("_order") is not None else 9999,
                        x["name"].lower(),
                    )
                )

            # Limpar chave de ordenação temporária
            for m in models:
                m.pop("_order", None)

        # 5. Ordenar as pastas globalmente
        if self._global_order:

            def folder_sort_key(folder):
                try:
                    idx = self._global_order.index(folder["app_label"])
                    return (0, idx, folder["name"].lower())
                except ValueError:
                    custom_ord = folder.get("order")
                    return (
                        1,
                        custom_ord if custom_ord is not None else 9999,
                        folder["name"].lower(),
                    )

            active_folders.sort(key=folder_sort_key)
        else:
            active_folders.sort(
                key=lambda x: (
                    x.get("order") if x.get("order") is not None else 9999,
                    x["name"].lower(),
                )
            )

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
    app_label,
    name=None,
    icon=None,
    app_url=None,
    order=None,
    permission=None,
    check=None,
):
    return registry.register_folder(
        app_label, name, icon, app_url, order, permission, check
    )


def register_item(
    app_label, name, url, icon=None, order=None, permission=None, check=None
):
    return registry.register_item(app_label, name, url, icon, order, permission, check)


def set_order(order_list):
    registry.set_order(order_list)


def set_items_order(app_label, order_list):
    registry.set_items_order(app_label, order_list)


def add_reorder_callback(callback):
    registry.add_reorder_callback(callback)


def get_menu_list(request):
    return registry.get_menu_list(request)


def autodiscover():
    autodiscover_modules("menus")
