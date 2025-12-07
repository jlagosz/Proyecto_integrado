from django import template

register = template.Library()

@register.simple_tag(takes_context=True)
def url_replace(context, **kwargs):
    """
    Toma los parámetros actuales de la URL (ej: ?q=juan&page=1)
    y reemplaza o agrega los nuevos (ej: sort=rut), devolviendo la URL completa.
    Esto permite que BUSCAR y ORDENAR funcionen juntos.
    """
    query = context['request'].GET.copy()
    for key, value in kwargs.items():
        query[key] = value
    return query.urlencode()

@register.simple_tag(takes_context=True)
def sort_icon(context, field_name):
    """
    Muestra la flechita correcta dependiendo si se está ordenando
    ascendente o descendente por ese campo.
    """
    current_sort = context['request'].GET.get('sort', '')
    
    if current_sort == field_name:
        return 'bi-sort-down-alt'  # A-Z
    elif current_sort == f'-{field_name}':
        return 'bi-sort-up'        # Z-A
    
    return 'bi-arrow-down-up'      # Neutro

@register.simple_tag(takes_context=True)
def next_sort(context, field_name):
    """
    Calcula qué debe pasar al hacer clic:
    Si ya está ordenado por 'nombre', el siguiente clic será '-nombre' (descendente).
    """
    current_sort = context['request'].GET.get('sort', '')
    if current_sort == field_name:
        return f'-{field_name}'
    return field_name