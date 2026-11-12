import datetime
from urllib.parse import parse_qsl, urlencode


import django
from django.contrib.admin.templatetags.admin_urls import add_preserved_filters
from django.contrib.admin.utils import (
    display_for_field,
    display_for_value,
    label_for_field,
    lookup_field,
)
from django.contrib.admin.views.main import ALL_VAR, ORDER_VAR, PAGE_VAR, SEARCH_VAR
from django.core.exceptions import ObjectDoesNotExist
from django.db import models
from django.db.models.constants import LOOKUP_SEP
from django.template import Library
from django.urls import NoReverseMatch
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.contrib.admin.templatetags.base import InclusionAdminNode

register = Library()


def _coerce_field_name(field_name, field_index):
    """
    Coerce a field_name (which may be a callable) to a string.
    """
    if callable(field_name):
        if field_name.__name__ == "<lambda>":
            return "lambda" + str(field_index)
        else:
            return field_name.__name__
    return field_name


def result_headers(cl):
    """
    Generate the list column headers.
    """
    ordering_field_columns = cl.get_ordering_field_columns()
    for i, field_name in enumerate(cl.list_display):
        text, attr = label_for_field(
            field_name, cl.model, model_admin=cl.model_admin, return_attr=True
        )
        is_field_sortable = cl.sortable_by is None or field_name in cl.sortable_by
        if attr:
            field_name = _coerce_field_name(field_name, i)
            # Potentially not sortable

            # a coluna de seleção (action_checkbox) é do <dsgovbr-tabela>
            if field_name == "action_checkbox":
                continue

            admin_order_field = getattr(attr, "admin_order_field", None)
            # Set ordering for attr that is a property, if defined.
            if isinstance(attr, property) and hasattr(attr, "fget"):
                admin_order_field = getattr(attr.fget, "admin_order_field", None)
            if not admin_order_field and LOOKUP_SEP not in field_name:
                is_field_sortable = False

        if not is_field_sortable:
            # Not sortable
            yield {
                "text": text,
                "class_attrib": format_html(' class="column-{}"', field_name),
                "sortable": False,
            }
            continue

        # OK, it is sortable if we got this far
        th_classes = ["sortable", "column-{}".format(field_name)]
        order_type = ""
        new_order_type = "asc"
        sort_priority = 0
        # Is it currently being sorted on?
        is_sorted = i in ordering_field_columns
        if is_sorted:
            order_type = ordering_field_columns.get(i).lower()
            sort_priority = list(ordering_field_columns).index(i) + 1
            th_classes.append("sorted %sending" % order_type)
            new_order_type = {"asc": "desc", "desc": "asc"}[order_type]

        # build new ordering param
        o_list_primary = []  # URL for making this field the primary sort
        o_list_remove = []  # URL for removing this field from sort
        o_list_toggle = []  # URL for toggling order type for this field

        def make_qs_param(t, n):
            return ("-" if t == "desc" else "") + str(n)

        for j, ot in ordering_field_columns.items():
            if j == i:  # Same column
                param = make_qs_param(new_order_type, j)
                # We want clicking on this header to bring the ordering to the
                # front
                o_list_primary.insert(0, param)
                o_list_toggle.append(param)
                # o_list_remove - omit
            else:
                param = make_qs_param(ot, j)
                o_list_primary.append(param)
                o_list_toggle.append(param)
                o_list_remove.append(param)

        if i not in ordering_field_columns:
            o_list_primary.insert(0, make_qs_param(new_order_type, i))

        yield {
            "text": text,
            "sortable": True,
            "sorted": is_sorted,
            "ascending": order_type == "asc",
            "sort_priority": sort_priority,
            "url_primary": cl.get_query_string({ORDER_VAR: ".".join(o_list_primary)}),
            "url_remove": cl.get_query_string({ORDER_VAR: ".".join(o_list_remove)}),
            "url_toggle": cl.get_query_string({ORDER_VAR: ".".join(o_list_toggle)}),
            "class_attrib": (
                format_html(' class="{}"', " ".join(th_classes)) if th_classes else ""
            ),
        }


def items_for_result(cl, result, form):
    """
    Generate the actual list of data.
    """

    def link_in_col(is_first, field_name, cl):
        if cl.list_display_links is None:
            return False
        if is_first and not cl.list_display_links:
            return True
        return field_name in cl.list_display_links

    first = True
    pk = cl.lookup_opts.pk.attname
    for field_index, field_name in enumerate(cl.list_display):
        if field_name == "action_checkbox":
            # a coluna de seleção é do <dsgovbr-tabela>
            continue
        empty_value_display = cl.model_admin.get_empty_value_display()
        row_classes = ["field-%s" % _coerce_field_name(field_name, field_index)]
        link_to_changelist = link_in_col(first, field_name, cl)
        try:
            f, attr, value = lookup_field(field_name, result, cl.model_admin)
        except ObjectDoesNotExist:
            result_repr = empty_value_display
        else:
            empty_value_display = getattr(
                attr, "empty_value_display", empty_value_display
            )
            if isinstance(value, str) and value.strip() == "":
                value = ""
            if f is None or f.auto_created:
                boolean = getattr(attr, "boolean", False)
                # Set boolean for attr that is a property, if defined.
                if isinstance(attr, property) and hasattr(attr, "fget"):
                    boolean = getattr(attr.fget, "boolean", False)
                result_repr = display_for_value(value, empty_value_display, boolean)
                if isinstance(value, (datetime.date, datetime.time)):
                    row_classes.append("nowrap")
            else:
                if isinstance(f.remote_field, models.ManyToOneRel):
                    field_val = getattr(result, f.name)
                    if field_val is None:
                        result_repr = empty_value_display
                    else:
                        result_repr = field_val
                else:
                    result_repr = display_for_field(
                        value,
                        f,
                        empty_value_display,
                        avoid_link=link_to_changelist,
                    )
                if isinstance(
                    f, (models.DateField, models.TimeField, models.ForeignKey)
                ):
                    row_classes.append("nowrap")
        row_class = mark_safe(' class="%s"' % " ".join(row_classes))
        # If list_display_links not defined, add the link tag to the first
        # field
        if link_to_changelist:
            table_tag = "td" if first else "td"
            first = False

            # Display link to the result's change_view if the url exists, else
            # display just the result's representation.
            try:
                url = cl.url_for_result(result)
            except NoReverseMatch:
                link_or_text = result_repr
            else:
                url = add_preserved_filters(
                    {"preserved_filters": cl.preserved_filters, "opts": cl.opts}, url
                )
                # Convert the pk to something that can be used in JavaScript.
                # Problem cases are non-ASCII strings.
                if cl.to_field:
                    attr = str(cl.to_field)
                else:
                    attr = pk
                value = result.serializable_value(attr)
                link_or_text = format_html(
                    '<a href="{}"{}>{}</a>',
                    url,
                    (
                        format_html(' data-popup-opener="{}"', value)
                        if cl.is_popup
                        else ""
                    ),
                    result_repr,
                )

            yield format_html(
                "<{}{}>{}</{}>", table_tag, row_class, link_or_text, table_tag
            )
        else:
            # By default the fields come from ModelAdmin.list_editable, but if
            # we pull the fields out of the form instead of list_editable
            # custom admin can provide fields on a per request basis
            if (
                form
                and field_name in form.fields
                and not (
                    field_name == cl.model._meta.pk.name
                    and form[cl.model._meta.pk.name].is_hidden
                )
            ):
                bf = form[field_name]
                result_repr = mark_safe(str(bf.errors) + str(bf))
            yield format_html("<td{}>{}</td>", row_class, result_repr)
    if form and not form[cl.model._meta.pk.name].is_hidden:
        yield format_html("<td>{}</td>", form[cl.model._meta.pk.name])


class ResultList(list):
    """
    Wrapper class used to return items in a list_editable changelist, annotated
    with the form object for error reporting purposes. Needed to maintain
    backwards compatibility with existing admin templates.
    """

    def __init__(self, form, *items, pk=None):
        self.form = form
        self.pk = pk  # valor do data-valor da linha (a seleção do <dsgovbr-tabela>)
        super().__init__(*items)


def results(cl):
    if cl.formset:
        for res, form in zip(cl.result_list, cl.formset.forms):
            yield ResultList(form, items_for_result(cl, res, form), pk=str(res.pk))
    else:
        for res in cl.result_list:
            yield ResultList(None, items_for_result(cl, res, None), pk=str(res.pk))


def result_hidden_fields(cl):
    if cl.formset:
        for res, form in zip(cl.result_list, cl.formset.forms):
            if form[cl.model._meta.pk.name].is_hidden:
                yield mark_safe(form[cl.model._meta.pk.name])


def result_list(cl):
    """
    Display the headers and data list together.
    """
    headers = list(result_headers(cl))
    num_sorted_fields = 0
    for h in headers:
        if h["sortable"] and h["sorted"]:
            num_sorted_fields += 1
    return {
        "cl": cl,
        "result_hidden_fields": list(result_hidden_fields(cl)),
        "result_headers": headers,
        "num_sorted_fields": num_sorted_fields,
        "results": list(results(cl)),
    }


@register.tag(name="dsgovbr_result_list")
def result_list_tag(parser, token):
    # Django 6.1 passou a exigir o nome da tag como primeiro argumento
    nome = ("dsgovbr_result_list",) if django.VERSION >= (6, 1) else ()
    return InclusionAdminNode(
        *nome,
        parser,
        token,
        func=result_list,
        template_name="change_list_dsgovbr_results.html",
        takes_context=False,
    )


@register.simple_tag
def dsgovbr_pagina_href(cl) -> str:
    """Modelo de URL das páginas para o ``paginacao-href`` (``{pagina}`` vira o número).

    Mantém a busca, os filtros e a ordenação atuais, como o ``get_query_string`` do
    ChangeList.
    """
    marcador = "DSGOVBRPAGINA"
    return cl.get_query_string({PAGE_VAR: marcador}).replace(marcador, "{pagina}")


@register.simple_tag
def dsgovbr_filtros(cl) -> dict:
    """Filtros do ChangeList no formato do ``<dsgovbr-filtro>``.

    Retorna ``{"filtros": [...], "parametros": [...], "busca": "q"}`` (``busca`` é o nome do parâmetro da busca). Cada filtro tem ``nome``
    (único na página), ``rotulo`` e ``opcoes``. O ``valor`` de cada opção são os
    parâmetros de query da própria opção (``urlencode``), pois uma opção do Django
    pode ter vários (intervalo de data: ``__gte`` e ``__lt``). A opção "Todos" não
    entra: sem opção marcada o filtro sai da URL. ``parametros`` lista todos os
    parâmetros de filtro, para a cola JS tirá-los da URL antes de aplicar a escolha.
    """
    filtros = []
    parametros: list[str] = []
    for indice, spec in enumerate(cl.filter_specs, start=1):
        esperados = list(spec.expected_parameters() or [])
        parametros.extend(p for p in esperados if p not in parametros)
        opcoes = []
        for choice in spec.choices(cl):
            consulta = parse_qsl(
                (choice.get("query_string") or "").lstrip("?"),
                keep_blank_values=True,
            )
            proprios = [(k, v) for k, v in consulta if k in esperados]
            if not proprios:
                continue
            opcoes.append(
                {
                    "valor": urlencode(proprios),
                    "texto": str(choice["display"]),
                    "selecionada": bool(choice.get("selected")),
                }
            )
        if opcoes:
            filtros.append(
                {
                    "nome": f"filtro-{indice}",
                    "rotulo": str(spec.title).capitalize(),
                    "opcoes": opcoes,
                }
            )
    return {"filtros": filtros, "parametros": parametros, "busca": SEARCH_VAR}


@register.simple_tag
def dsgovbr_mostrar_todos_href(cl) -> str:
    """URL do "Mostrar todos" (vazia quando não há o que mostrar), como o ``pagination`` do Django."""
    if cl.can_show_all and not cl.show_all and cl.multi_page:
        return cl.get_query_string({ALL_VAR: ""})
    return ""
