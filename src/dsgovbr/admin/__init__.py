from collections.abc import Callable, Generator
from django.http import HttpRequest, HttpResponse
from dataclasses import dataclass
from django.conf import settings
from django.forms import Media
from django.utils.text import capfirst
from django.urls import path, reverse
from django.shortcuts import redirect
from django.db.models import Model
from django.contrib.admin import ModelAdmin, AdminSite
from django.contrib.admin.views.main import ChangeList
from django.contrib.admin.utils import quote, unquote
from django.contrib.admin.options import IS_POPUP_VAR, TO_FIELD_VAR, flatten_fieldsets
from django.contrib.admin.helpers import AdminErrorList, AdminForm, InlineAdminFormSet
from django.contrib.admin.exceptions import DisallowedModelAdminToField, NotRegistered
from django.core.exceptions import PermissionDenied


@dataclass(frozen=True)
class ActionSpec:
    label: str
    handler: str
    icon: str = ""
    css_class: str = ""
    permission: str | None = None
    authorize: Callable | None = None
    admin: Callable | None = None

    def is_allowed(self, admin: ModelAdmin, request: HttpRequest) -> bool:
        return (self.permission and request.user.has_perm(self.permission)) or (
            self.authorize and self.authorize(request)
        )

    @property
    def admin_url_name(self) -> str:
        """
        Retorna o nome da URL admin customizada para este handler.
        Uso: action.get_admin_url_name(admin)
        """
        return f"admin:{self.admin.opts.app_label}_{self.admin.opts.model_name}_{self.handler}"


@dataclass(frozen=True)
class ObjectToolSpec(ActionSpec):
    pass


@dataclass(frozen=True)
class InstanceActionSpec(ActionSpec):
    pass


class DSGovBrChangeList(ChangeList):
    def __init__(
        self,
        request,
        model,
        list_display,
        list_display_links,
        list_filter,
        date_hierarchy,
        search_fields,
        list_select_related,
        list_per_page,
        list_max_show_all,
        list_editable,
        model_admin,
        sortable_by,
        search_help_text,
    ):
        super().__init__(
            request,
            model,
            list_display,
            list_display_links,
            list_filter,
            date_hierarchy,
            search_fields,
            list_select_related,
            list_per_page,
            list_max_show_all,
            list_editable,
            model_admin,
            sortable_by,
            search_help_text,
        )
        self.title = str(capfirst(model_admin.opts.verbose_name_plural))

    def url_for_result(self, result):
        return reverse(
            f"admin:{self.opts.app_label}_{self.opts.model_name}_redirect",
            args=(quote(getattr(result, self.pk_attname)),),
            current_app=self.model_admin.admin_site.name,
        )


class DSGovBrBaseModelAdmin(ModelAdmin):
    list_filter = []
    object_tool_actions: list[ObjectToolSpec] | None = None
    instance_actions: list[InstanceActionSpec] | None = None
    default_view: str = "preview"

    def get_custom_urls(self):
        # Gera rotas para todos métodos do self que terminam com _customview
        import inspect

        urls = []
        for attr_name in dir(self):
            if attr_name.endswith("_customview") and callable(getattr(self, attr_name)):
                verb = attr_name[: -len("_customview")]
                method = getattr(self, attr_name)
                sig = inspect.signature(method)
                params = list(sig.parameters.values())
                # param 0 é request, param 1 pode ser object_id
                if len(params) > 1 and params[1].name == "object_id":
                    route = f"<path:object_id>/{verb}/"
                else:
                    route = f"{verb}/"
                urls.append(
                    path(
                        route,
                        self.admin_site.admin_view(method),
                        name=f"{self.opts.app_label}_{self.opts.model_name}_{verb}",
                    )
                )
        return urls

    def get_urls(self):

        urls = []
        info = self.opts.app_label, self.opts.model_name
        for _path in super().get_urls():
            if str(getattr(_path, "pattern", "")) != "<path:object_id>/":
                urls.append(_path)
            else:
                urls.append(
                    path(
                        "<path:object_id>/",
                        self.admin_site.admin_view(self.redirect_view),
                        name=f"{info[0]}_{info[1]}_redirect",
                    )
                )

        return self.get_custom_urls() + urls

    def get_object_tool_actions(self, request: HttpRequest) -> list[ObjectToolSpec]:
        return []

    def get_valid_object_tools_actions(
        self, request: HttpRequest
    ) -> Generator[ObjectToolSpec, None, None]:
        for object_tool in self.get_object_tool_actions(request):
            if not isinstance(object_tool, ObjectToolSpec):
                raise TypeError(f"{object_tool} precisa ser ObjectToolSpec")
            if object_tool.is_allowed(self, request):
                yield object_tool

    def get_changelist(self, request, **kwargs):
        return DSGovBrChangeList

    def changelist_view(
        self, request: HttpRequest, extra_context: dict | None = None
    ) -> HttpResponse:
        extra_context = extra_context or {}
        extra_context["object_tool_actions"] = self.get_valid_object_tools_actions(
            request
        )
        return super().changelist_view(request, extra_context=extra_context)

    def redirect_view(
        self,
        request: HttpRequest,
        object_id: str | int,
        form_url: str = "",
        extra_context: dict | None = None,
    ) -> HttpResponse:

        _default_view = getattr(self, "default_view", "preview")
        return redirect(
            f"admin:{self.opts.app_label}_{self.opts.model_name}_{_default_view}",
            object_id=object_id,
        )

    def preview_customview(
        self,
        request: HttpRequest,
        object_id: str | int,
        form_url: str = "",
        extra_context: dict | None = None,
    ) -> HttpResponse:
        to_field = request.POST.get(TO_FIELD_VAR, request.GET.get(TO_FIELD_VAR))
        if to_field and not self.to_field_allowed(request, to_field):
            raise DisallowedModelAdminToField(
                f"The field {to_field} cannot be referenced."
            )
        obj = self.get_object(request, unquote(object_id), to_field)
        try:
            related_modeladmin = self.admin_site.get_model_admin(obj.__class__)
        except NotRegistered:
            wrapper_kwargs = {}
        else:
            wrapper_kwargs = {
                "can_add_related": related_modeladmin.has_add_permission(request),
                "can_change_related": related_modeladmin.has_change_permission(request),
                "can_delete_related": related_modeladmin.has_delete_permission(request),
                "can_view_related": related_modeladmin.has_view_permission(request),
            }

        if not self.has_view_or_change_permission(request, obj):
            raise PermissionDenied

        request.in_view_mode = True

        fieldsets = self.get_fieldsets(request, obj)
        ModelForm = self.get_form(
            request, obj, change=False, fields=flatten_fieldsets(fieldsets)
        )
        form = ModelForm(instance=obj)
        formsets, inline_instances = self._create_formsets(request, obj, change=True)

        # form = self._get_form_for_get_fields(request, obj)
        # return [*form.base_fields, *self.get_readonly_fields(request, obj)]
        readonly_fields = [*form.base_fields, *self.get_readonly_fields(request, obj)]
        admin_form = AdminForm(
            form, list(fieldsets), {}, readonly_fields, model_admin=self
        )
        media = self.media + admin_form.media

        inline_formsets = self.get_inline_formsets(
            request, formsets, inline_instances, obj
        )
        # inline_formsets = []
        for inline_formset in inline_formsets:
            media += inline_formset.media
            inline_formset.readonly_fields = flatten_fieldsets(inline_formset.fieldsets)

        can_add_related = wrapper_kwargs.get("can_add_related", False)
        can_delete_related = wrapper_kwargs.get("can_delete_related", False)
        can_change_related = wrapper_kwargs.get("can_change_related", False)
        can_view_related = wrapper_kwargs.get("can_view_related", False)

        context = {
            **self.admin_site.each_context(request),
            "title": str(capfirst(self.opts.verbose_name_plural)),
            "subtitle": str(obj) if obj else None,
            "adminform": admin_form,
            "object_id": object_id,
            "original": obj,
            "is_popup": IS_POPUP_VAR in request.POST or IS_POPUP_VAR in request.GET,
            "to_field": to_field,
            "media": media,
            "inline_admin_formsets": inline_formsets,
            "errors": AdminErrorList(form, formsets),
            "preserved_filters": self.get_preserved_filters(request),
            "has_delete_permission": can_delete_related,
            "show_delete": can_delete_related,
            "show_delete_link": can_delete_related,
            "can_delete_related": can_delete_related,
            "has_add_permission": can_add_related,
            "show_change": can_change_related,
            "can_change_related": can_change_related,
            "show_save": False,
            "show_save_as_new": False,
            "show_save_and_add_another": False,
            "show_save_and_continue": False,
            "show_change_form_export": True,
            "can_view_related": can_view_related,
        }

        context.update(extra_context or {})

        return self.render_change_form(
            request, context, add=False, change=False, obj=obj, form_url=form_url
        )

    def get_inline_formsets(self, request, formsets, inline_instances, obj=None):
        # Edit permissions on parent model are required for editable inlines.
        if getattr(request, "in_view_mode", False):
            can_edit_parent = False
        else:
            can_edit_parent = (
                self.has_change_permission(request, obj)
                if obj
                else self.has_add_permission(request)
            )

        inline_admin_formsets = []
        for inline, formset in zip(inline_instances, formsets):
            fieldsets = list(inline.get_fieldsets(request, obj))
            readonly = list(inline.get_readonly_fields(request, obj))
            if can_edit_parent:
                has_add_permission = inline.has_add_permission(request, obj)
                has_change_permission = inline.has_change_permission(request, obj)
                has_delete_permission = inline.has_delete_permission(request, obj)
            else:
                # Disable all edit-permissions, and override formset settings.
                has_add_permission = has_change_permission = has_delete_permission = (
                    False
                )
                formset.extra = formset.max_num = 0
            has_view_permission = inline.has_view_permission(request, obj)
            prepopulated = dict(inline.get_prepopulated_fields(request, obj))
            inline_admin_formset = InlineAdminFormSet(
                inline,
                formset,
                fieldsets,
                prepopulated,
                readonly,
                model_admin=self,
                has_add_permission=has_add_permission,
                has_change_permission=has_change_permission,
                has_delete_permission=has_delete_permission,
                has_view_permission=has_view_permission,
            )
            inline_admin_formsets.append(inline_admin_formset)
        return inline_admin_formsets

    def get_instance_action_allowed(
        self, request: HttpRequest, instance: Model, action: InstanceActionSpec
    ) -> bool:
        return (
            action.permission is None or request.user.has_perm(action.permission)
        ) and (action.authorize is None or action.authorize(request, instance))

    def get_instance_actions(
        self, request: HttpRequest, instance: Model
    ) -> list[InstanceActionSpec] | None:
        return [
            a
            for a in (self.instance_actions or [])
            if self.is_valid_handler(a)
            and self.get_instance_action_allowed(request, instance, a)
        ]

    def is_valid_handler(self, a: ActionSpec) -> bool:
        return hasattr(self, a.handler) and callable(getattr(self, a.handler))

    def get_handler(self, spec: ActionSpec) -> Callable | None:
        return (
            getattr(self, spec.handler)
            if hasattr(self, spec.handler) and callable(getattr(self, spec.handler))
            else None
        )

    @property
    def media(self):
        parent_media = super().media if hasattr(super(), "media") else Media()
        extra = "" if settings.DEBUG else ".min"
        js = [
            "vendor/jquery/jquery%s.js" % extra,
            "jquery.init.js",
            "core.js",
            "admin/RelatedObjectLookups.js",
            # "actions.js", # Este arquivo causa problema pois não usamos neste tema o padrão do django admin de actions
            "urlify.js",
            "prepopulate.js",
            "vendor/xregexp/xregexp%s.js" % extra,
        ]
        return (
            parent_media
            + Media(js=["admin/js/%s" % url for url in js])
            + _select2_media(extra)
        )


def _select2_media(extra: str) -> Media:
    """Select2 do admin quando ``DSGOVBR_FORMS["select2_todos_fk"]`` está ligado.

    Mesma ordem do ``AutocompleteMixin.media`` do Django (Select2 entre o jQuery
    e o ``jquery.init.js``), para o merge do ``Media`` não duplicar os arquivos
    nas páginas que já têm ``autocomplete_fields``. O ``autocomplete.css`` do
    admin fica de fora: o tema "dsgovbr" do Select2 vem do ``dsgovbr.scss``.
    """
    from django.contrib.admin.widgets import get_select2_language

    from dsgovbr.context_processors import forms_settings

    if not forms_settings().get("select2_todos_fk"):
        return Media()
    idioma = get_select2_language()
    js = [
        "admin/js/vendor/jquery/jquery%s.js" % extra,
        "admin/js/vendor/select2/select2.full%s.js" % extra,
    ]
    if idioma:
        js.append("admin/js/vendor/select2/i18n/%s.js" % idioma)
    js.append("admin/js/jquery.init.js")
    return Media(
        js=js,
        css={"screen": ["admin/css/vendor/select2/select2%s.css" % extra]},
    )


class DSGovBrAdminSite(AdminSite):
    site_header = getattr(settings, "PROJECT_COMPANY", "Minha empresa")

    def get_app_list(self, request, app_label=None):
        """
        Retorna a lista de menus unificada e customizada.
        """
        from dsgovbr.menus import get_menu_list

        menu_list = get_menu_list(request)
        if app_label:
            return [app for app in menu_list if app["app_label"] == app_label]
        return menu_list

    def get_cards_app_list(self, request, app_label=None):
        """
        Lista do Django (com as permissões do usuário) e os ícones de app e model,
        para os cards da página inicial e da página do app.
        """
        from dsgovbr.icons import app_icon, model_icon

        app_list = AdminSite.get_app_list(self, request, app_label)
        for app in app_list:
            app["icon"] = app_icon(app.get("app_label"))
            for model in app.get("models", []):
                model["icon"] = model_icon(model.get("model"), self)
        return app_list

    def index(self, request, extra_context=None):
        # o get_app_list deste site é o menu (todos os apps); os cards usam as permissões reais
        extra_context = {
            "app_list": self.get_cards_app_list(request),
            **(extra_context or {}),
        }
        return super().index(request, extra_context)

    def app_index(self, request, app_label, extra_context=None):
        from django.http import Http404

        app_list = self.get_cards_app_list(request, app_label)
        # o app_index do Django testa get_app_list (o menu, que pode ter pastas do
        # menus.py); a página do app só existe para quem vê algum model dele
        if not app_list:
            raise Http404("The requested admin page does not exist.")
        extra_context = {"app_list": app_list, **(extra_context or {})}
        return super().app_index(request, app_label, extra_context)
