from django import template

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
