from django import template

register = template.Library()


@register.filter
def format_starting_bid(value: str):
    return "{:,.2f}".format(value)
