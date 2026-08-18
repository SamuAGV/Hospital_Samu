from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Obtener un valor de un diccionario por su clave."""
    if dictionary is None:
        return 0
    if not isinstance(dictionary, dict):
        return 0
    return dictionary.get(key, 0)

@register.filter
def get_attr(obj, attr):
    """Obtener un atributo de un objeto por su nombre."""
    return getattr(obj, attr, None)