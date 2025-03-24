from django import template
import os

register = template.Library()

@register.filter
def basename(value):
    return os.path.basename(value)

@register.filter
def before_hash(value):
    """Devuelve la parte de la cadena antes del '#'."""
    return value.split("#")[0] if value else ""