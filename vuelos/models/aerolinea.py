from django.db import models
from django.urls import reverse


class Aerolinea(models.Model):
    nombre = models.CharField(max_length=100, unique=True)
    codigo_iata = models.CharField(max_length=3, unique=True)
    pais = models.CharField(max_length=60)
    activa = models.BooleanField(default=True)

    class Meta:
        ordering = ['nombre']
        verbose_name = 'aerolínea'
        verbose_name_plural = 'aerolíneas'

    def __str__(self):
        return f'{self.nombre} ({self.codigo_iata})'

    def get_absolute_url(self):
        return reverse('aerolinea_detail', kwargs={'pk': self.pk})
