from django.db import models
from django.urls import reverse


class Vuelo(models.Model):
    class Estado(models.TextChoices):
        PROGRAMADO = 'PRG', 'Programado'
        RETRASADO = 'RET', 'Retrasado'
        CANCELADO = 'CAN', 'Cancelado'
        COMPLETADO = 'COM', 'Completado'

    codigo = models.CharField(max_length=10, unique=True)
    aerolinea = models.ForeignKey(
        'vuelos.Aerolinea',
        on_delete=models.PROTECT,
        related_name='vuelos',
    )
    origen = models.CharField(max_length=80)
    destino = models.CharField(max_length=80)
    fecha_salida = models.DateTimeField()
    fecha_llegada = models.DateTimeField()
    precio = models.DecimalField(max_digits=8, decimal_places=2)
    asientos = models.PositiveIntegerField(default=150)
    estado = models.CharField(
        max_length=3,
        choices=Estado.choices,
        default=Estado.PROGRAMADO,
    )

    class Meta:
        ordering = ['fecha_salida']
        verbose_name = 'vuelo'
        verbose_name_plural = 'vuelos'

    def __str__(self):
        return f'{self.codigo}: {self.origen} → {self.destino}'

    def get_absolute_url(self):
        return reverse('vuelo_detail', kwargs={'pk': self.pk})

    @property
    def asientos_ocupados(self):
        total = 0
        for reserva in self.reservas.exclude(estado='CAN'):
            total += reserva.pasajeros.count()
        return total

    @property
    def asientos_disponibles(self):
        return self.asientos - self.asientos_ocupados
