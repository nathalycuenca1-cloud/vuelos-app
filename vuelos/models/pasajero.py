from django.conf import settings
from django.db import models
from django.urls import reverse


class Pasajero(models.Model):
    nombres = models.CharField(max_length=80)
    apellidos = models.CharField(max_length=80)
    documento = models.CharField(max_length=20, unique=True)
    email = models.EmailField()
    fecha_nacimiento = models.DateField()
    nacionalidad = models.CharField(max_length=60, default='Ecuatoriana')
    creado_por = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='pasajeros_creados',
    )

    class Meta:
        ordering = ['apellidos', 'nombres']
        verbose_name = 'pasajero'
        verbose_name_plural = 'pasajeros'

    def __str__(self):
        return f'{self.apellidos} {self.nombres}'

    def get_absolute_url(self):
        return reverse('pasajero_detail', kwargs={'pk': self.pk})

    @property
    def nombre_completo(self):
        return f'{self.nombres} {self.apellidos}'