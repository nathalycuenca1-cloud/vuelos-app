from vuelos.models import Pasajero


def es_administrador(user):
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    return user.groups.filter(name='administradores').exists()


def puede_modificar(user, objeto):
    if not user.is_authenticated:
        return False
    if es_administrador(user):
        return True
    return objeto.creado_por_id == user.id


def pasajeros_visibles(user):
    if es_administrador(user):
        return Pasajero.objects.all()
    if not user.is_authenticated:
        return Pasajero.objects.none()
    return Pasajero.objects.filter(creado_por=user)