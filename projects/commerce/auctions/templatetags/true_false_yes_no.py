from django import template

register = template.Library()


@register.filter
def true_false_yes_no(value: bool):
    return "Yes" if value else "No"
