def es_administrador(user):
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    return user.groups.filter(name='administradores').exists()


def puede_modificar(user, reserva):
    if not user.is_authenticated:
        return False
    if es_administrador(user):
        return True
    return reserva.creado_por_id == user.id
