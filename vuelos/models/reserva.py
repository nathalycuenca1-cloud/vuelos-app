from decimal import Decimal

from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils import timezone


class Reserva(models.Model):
    class Clase(models.TextChoices):
        ECONOMICA = 'ECO', 'Económica'
        EJECUTIVA = 'EJE', 'Ejecutiva'
        PRIMERA = 'PRI', 'Primera clase'

    class Estado(models.TextChoices):
        PENDIENTE = 'PEN', 'Pendiente'
        CONFIRMADA = 'CON', 'Confirmada'
        CANCELADA = 'CAN', 'Cancelada'

    FACTORES_CLASE = {
        'ECO': Decimal('1.00'),
        'EJE': Decimal('1.80'),
        'PRI': Decimal('2.60'),
    }

    codigo = models.CharField(max_length=12, unique=True)
    vuelo = models.ForeignKey(
        'vuelos.Vuelo',
        on_delete=models.PROTECT,
        related_name='reservas',
    )
    pasajeros = models.ManyToManyField(
        'vuelos.Pasajero',
        related_name='reservas',
    )
    clase = models.CharField(
        max_length=3,
        choices=Clase.choices,
        default=Clase.ECONOMICA,
    )
    estado = models.CharField(
        max_length=3,
        choices=Estado.choices,
        default=Estado.PENDIENTE,
    )
    fecha_reserva = models.DateField(default=timezone.localdate)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reservas_creadas',
    )

    class Meta:
        ordering = ['-fecha_reserva', '-id']
        verbose_name = 'reserva'
        verbose_name_plural = 'reservas'

    def __str__(self):
        return f'Reserva {self.codigo} - {self.vuelo.codigo}'

    def get_absolute_url(self):
        return reverse('reserva_detail', kwargs={'pk': self.pk})

    @classmethod
    def calcular_total(cls, vuelo, clase, cantidad_pasajeros):
        total = vuelo.precio * cantidad_pasajeros * cls.FACTORES_CLASE[clase]
        return total.quantize(Decimal('0.01'))