from datetime import date, datetime, timedelta
from decimal import Decimal

from django.contrib.auth.models import Group, User
from django.core.management import call_command
from django.core.management.base import BaseCommand
from django.utils import timezone

from vuelos.grupos import crear_grupos
from vuelos.models import Aerolinea, Pasajero, Reserva, Vuelo

AEROLINEAS = [
    ('LATAM Airlines', 'LA', 'Chile'),
    ('Avianca', 'AV', 'Colombia'),
    ('Copa Airlines', 'CM', 'Panamá'),
    ('Iberia', 'IB', 'España'),
    ('American Airlines', 'AA', 'Estados Unidos'),
    ('Sky Airline', 'H2', 'Chile'),
]

VUELOS = [
    ('LA1450', 'LA', 'Quito (UIO)', 'Lima (LIM)', 1, '185.50', 'PRG'),
    ('AV0231', 'AV', 'Quito (UIO)', 'Bogotá (BOG)', 2, '142.00', 'PRG'),
    ('CM0377', 'CM', 'Guayaquil (GYE)', 'Ciudad de Panamá (PTY)', 3, '230.75', 'PRG'),
    ('IB6402', 'IB', 'Quito (UIO)', 'Madrid (MAD)', 5, '845.00', 'PRG'),
    ('AA0922', 'AA', 'Guayaquil (GYE)', 'Miami (MIA)', 4, '410.30', 'RET'),
    ('H20507', 'H2', 'Lima (LIM)', 'Santiago (SCL)', 6, '120.90', 'PRG'),
    ('LA2208', 'LA', 'Santiago (SCL)', 'Quito (UIO)', 7, '295.40', 'PRG'),
    ('AV0415', 'AV', 'Bogotá (BOG)', 'Guayaquil (GYE)', 8, '155.60', 'CAN'),
]

PASAJEROS = [
    ('Nathaly', 'Cuenca', '1712345678', 'nathaly.cuenca@example.com', date(2003, 5, 14), 'Ecuatoriana', 'consultor1'),
    ('Carlos', 'Andrade', '1723456789', 'carlos.andrade@example.com', date(1990, 2, 3), 'Ecuatoriana', 'consultor1'),
    ('María', 'Salazar', '0912345670', 'maria.salazar@example.com', date(1985, 11, 22), 'Ecuatoriana', 'consultor1'),
    ('Luis', 'Pérez', 'PA4455221', 'luis.perez@example.com', date(1978, 7, 9), 'Colombiana', 'consultor2'),
    ('Ana', 'Gómez', 'PA7788990', 'ana.gomez@example.com', date(1995, 1, 30), 'Peruana', 'administrador1'),
    ('Diego', 'Torres', '1798765432', 'diego.torres@example.com', date(2000, 9, 18), 'Ecuatoriana', 'administrador1'),
    ('Valeria', 'Mora', '1756789012', 'valeria.mora@example.com', date(1998, 4, 6), 'Ecuatoriana', 'consultor2'),
]

USUARIOS = [
    ('admin', 'Admin12345*', 'superusuario'),
    ('administrador1', 'Admin12345*', 'administradores'),
    ('consultor1', 'Consultor12345*', 'consultores'),
    ('consultor2', 'Consultor12345*', 'consultores'),
]

FACTORES_CLASE = {'ECO': Decimal('1.00'), 'EJE': Decimal('1.80'), 'PRI': Decimal('2.60')}


class Command(BaseCommand):
    help = 'Crea grupos, usuarios de prueba y al menos cinco registros por tabla.'

    def handle(self, *args, **options):
        call_command('migrate', verbosity=0)
        administradores, consultores = crear_grupos()
        usuarios = self.crear_usuarios(administradores, consultores)
        aerolineas = self.crear_aerolineas()
        vuelos = self.crear_vuelos(aerolineas)
        pasajeros = self.crear_pasajeros(usuarios)
        self.crear_reservas(vuelos, pasajeros, usuarios)
        self.stdout.write(self.style.SUCCESS('Datos de prueba cargados correctamente.'))

    def crear_usuarios(self, administradores, consultores):
        usuarios = {}
        for username, clave, rol in USUARIOS:
            user, _ = User.objects.get_or_create(
                username=username,
                defaults={'email': f'{username}@example.com'},
            )
            user.set_password(clave)
            if rol == 'superusuario':
                user.is_staff = True
                user.is_superuser = True
            elif rol == 'administradores':
                user.groups.add(administradores)
            else:
                user.groups.add(consultores)
            user.save()
            usuarios[username] = user
        return usuarios

    def crear_aerolineas(self):
        aerolineas = {}
        for nombre, codigo, pais in AEROLINEAS:
            aerolinea, _ = Aerolinea.objects.get_or_create(
                codigo_iata=codigo,
                defaults={'nombre': nombre, 'pais': pais, 'activa': True},
            )
            aerolineas[codigo] = aerolinea
        return aerolineas

    def crear_vuelos(self, aerolineas):
        vuelos = []
        base = timezone.make_aware(datetime.combine(timezone.localdate() + timedelta(days=7), datetime.min.time()))
        for indice, (codigo, iata, origen, destino, dias, precio, estado) in enumerate(VUELOS):
            salida = base + timedelta(days=dias, hours=6 + indice)
            vuelo, _ = Vuelo.objects.get_or_create(
                codigo=codigo,
                defaults={
                    'aerolinea': aerolineas[iata],
                    'origen': origen,
                    'destino': destino,
                    'fecha_salida': salida,
                    'fecha_llegada': salida + timedelta(hours=3, minutes=30),
                    'precio': Decimal(precio),
                    'asientos': 150,
                    'estado': estado,
                },
            )
            vuelos.append(vuelo)
        return vuelos

    def crear_pasajeros(self, usuarios):
        pasajeros = []
        for nombres, apellidos, documento, email, nacimiento, nacionalidad, autor in PASAJEROS:
            pasajero, _ = Pasajero.objects.get_or_create(
                documento=documento,
                defaults={
                    'nombres': nombres,
                    'apellidos': apellidos,
                    'email': email,
                    'fecha_nacimiento': nacimiento,
                    'nacionalidad': nacionalidad,
                },
            )
            if pasajero.creado_por_id is None:
                pasajero.creado_por = usuarios[autor]
                pasajero.save(update_fields=['creado_por'])
            pasajeros.append(pasajero)
        return pasajeros

    def crear_reservas(self, vuelos, pasajeros, usuarios):
        plan = [
            ('RSV-0001', 0, [0], 'ECO', 'CON', 'consultor1'),
            ('RSV-0002', 1, [1, 2], 'EJE', 'CON', 'consultor1'),
            ('RSV-0003', 3, [3], 'PRI', 'PEN', 'consultor2'),
            ('RSV-0004', 2, [4, 5], 'ECO', 'PEN', 'administrador1'),
            ('RSV-0005', 4, [6], 'EJE', 'CAN', 'administrador1'),
            ('RSV-0006', 5, [3, 6], 'ECO', 'CON', 'consultor2'),
        ]
        for codigo, indice_vuelo, indices_pasajeros, clase, estado, autor in plan:
            vuelo = vuelos[indice_vuelo]
            total = vuelo.precio * len(indices_pasajeros) * FACTORES_CLASE[clase]
            reserva, creada = Reserva.objects.get_or_create(
                codigo=codigo,
                defaults={
                    'vuelo': vuelo,
                    'clase': clase,
                    'estado': estado,
                    'fecha_reserva': timezone.localdate(),
                    'total': total.quantize(Decimal('0.01')),
                    'creado_por': usuarios[autor],
                },
            )
            if creada:
                reserva.pasajeros.set([pasajeros[i] for i in indices_pasajeros])