from django import template

register = template.Library()

@register.filter
def range_custom(value):
    return range(value)
