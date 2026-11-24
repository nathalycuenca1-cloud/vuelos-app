from django import forms

from vuelos.models import Reserva


class ReservaForm(forms.ModelForm):
    class Meta:
        model = Reserva
        fields = ['codigo', 'vuelo', 'pasajeros', 'clase', 'estado', 'fecha_reserva', 'total']
        widgets = {
            'codigo': forms.TextInput(attrs={'placeholder': 'Ej. RSV-0001'}),
            'pasajeros': forms.CheckboxSelectMultiple(),
            'fecha_reserva': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
            'total': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
        }

    def clean_codigo(self):
        return self.cleaned_data['codigo'].strip().upper()

    def clean_total(self):
        total = self.cleaned_data['total']
        if total <= 0:
            raise forms.ValidationError('El total debe ser mayor que cero.')
        return total

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
        return datos
