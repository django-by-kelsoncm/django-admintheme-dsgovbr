from django import template
from django.utils.html import format_html
from django.utils.safestring import SafeString
from django.contrib.admin.views.main import PAGE_VAR

register = template.Library()


@register.filter
def first_word(value: str) -> str:
    return str(value).split(" ")[0]


@register.filter
def last_word(value: str) -> str:
    return str(value).split(" ")[0]


@register.filter
def user_letters(user):
    # return user.first_name[:1].upper() + user.last_name[:1].upper()
    return user.first_name[:1].upper()


@register.simple_tag
def page_item(cl, page) -> SafeString:
    """Item da paginação do Bootstrap (.page-item/.page-link) para a lista do admin."""
    if page == cl.paginator.ELLIPSIS:
        return format_html(
            '<li class="page-item disabled"><span class="page-link">{}</span></li>',
            page,
        )
    if page == cl.page_num:
        return format_html(
            '<li class="page-item active" aria-current="page">'
            '<span class="page-link">{}</span></li>',
            page,
        )
    return format_html(
        '<li class="page-item"><a class="page-link" href="{}">{}</a></li>',
        cl.get_query_string({PAGE_VAR: page}),
        page,
    )
