from django.contrib.auth.models import Group, Permission

MODELOS = ['aerolinea', 'vuelo', 'pasajero', 'reserva']


def crear_grupos():
    administradores, _ = Group.objects.get_or_create(name='administradores')
    consultores, _ = Group.objects.get_or_create(name='consultores')

    codigos_admin = []
    for modelo in MODELOS:
        for accion in ('add', 'change', 'delete', 'view'):
            codigos_admin.append(f'{accion}_{modelo}')
    permisos_admin = Permission.objects.filter(
        content_type__app_label='vuelos',
        codename__in=codigos_admin,
    )
    administradores.permissions.set(permisos_admin)

    codigos_consultor = [f'view_{modelo}' for modelo in MODELOS]
    codigos_consultor += [
        'add_reserva', 'change_reserva', 'delete_reserva',
        'add_pasajero', 'change_pasajero', 'delete_pasajero',
    ]
    permisos_consultor = Permission.objects.filter(
        content_type__app_label='vuelos',
        codename__in=codigos_consultor,
    )
    consultores.permissions.set(permisos_consultor)
    return administradores, consultores