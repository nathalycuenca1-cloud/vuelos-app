from django import forms

from vuelos.models import Pasajero, Reserva, Vuelo
from vuelos.permisos import es_administrador, pasajeros_visibles


class ReservaForm(forms.ModelForm):
    class Meta:
        model = Reserva
        fields = ['codigo', 'vuelo', 'pasajeros', 'clase', 'estado', 'fecha_reserva']
        widgets = {
            'codigo': forms.TextInput(attrs={'placeholder': 'Ej. RSV-0001'}),
            'pasajeros': forms.CheckboxSelectMultiple(),
            'fecha_reserva': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
        }

    def __init__(self, *args, user=None, **kwargs):
        super().__init__(*args, **kwargs)
        if user is not None:
            visibles = pasajeros_visibles(user)
            if self.instance.pk:
                actuales = self.instance.pasajeros.values_list('pk', flat=True)
                visibles = Pasajero.objects.filter(pk__in=list(visibles.values_list('pk', flat=True)) + list(actuales))
            self.fields['pasajeros'].queryset = visibles
            if not self.instance.pk and not es_administrador(user):
                propio = visibles.order_by('pk').first()
                if propio is not None:
                    self.initial['pasajeros'] = [propio.pk]
            self.fields['pasajeros'].help_text = 'Solo aparecen los pasajeros que usted registró.'

    def datos_total(self):
        return {
            'precios': {str(vuelo.pk): vuelo.precio for vuelo in Vuelo.objects.all()},
            'factores': Reserva.FACTORES_CLASE,
        }

    def clean_codigo(self):
        return self.cleaned_data['codigo'].strip().upper()

    def clean_pasajeros(self):
        pasajeros = self.cleaned_data['pasajeros']
        if pasajeros.count() < 1:
            raise forms.ValidationError('Seleccione al menos un pasajero.')
        return pasajeros

    def clean(self):
        datos = super().clean()
        vuelo = datos.get('vuelo')
        pasajeros = datos.get('pasajeros')
        if vuelo and pasajeros:
            ocupados = 0
            for reserva in vuelo.reservas.exclude(estado='CAN'):
                if self.instance.pk and reserva.pk == self.instance.pk:
                    continue
                ocupados += reserva.pasajeros.count()
            if ocupados + pasajeros.count() > vuelo.asientos:
                self.add_error('pasajeros', 'No hay asientos suficientes en este vuelo.')
            clase = datos.get('clase')
            if clase:
                self.instance.total = Reserva.calcular_total(vuelo, clase, pasajeros.count())
        return datos