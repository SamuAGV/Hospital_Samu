# apps/core/templatetags/custom_filters.py
from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """
    Devuelve el valor de un diccionario por su clave.
    Uso en templates: {{ dict|get_item:key }}
    """
    if dictionary is None:
        return None
    return dictionary.get(key)