from django import template

from vuelos.permisos import es_administrador, puede_modificar as _puede_modificar

register = template.Library()


@register.filter
def puede_modificar(reserva, user):
    return _puede_modificar(user, reserva)


@register.filter
def administrador(user):
    return es_administrador(user)
