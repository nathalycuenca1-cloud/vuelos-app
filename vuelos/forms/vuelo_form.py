from django import forms

from vuelos.models import Vuelo

FORMATO_FECHA_HORA = '%Y-%m-%dT%H:%M'


class VueloForm(forms.ModelForm):
    fecha_salida = forms.DateTimeField(
        input_formats=[FORMATO_FECHA_HORA],
        widget=forms.DateTimeInput(
            attrs={'type': 'datetime-local'},
            format=FORMATO_FECHA_HORA,
        ),
    )
    fecha_llegada = forms.DateTimeField(
        input_formats=[FORMATO_FECHA_HORA],
        widget=forms.DateTimeInput(
            attrs={'type': 'datetime-local'},
            format=FORMATO_FECHA_HORA,
        ),
    )

    class Meta:
        model = Vuelo
        fields = [
            'codigo', 'aerolinea', 'origen', 'destino',
            'fecha_salida', 'fecha_llegada', 'precio', 'asientos', 'estado',
        ]
        widgets = {
            'codigo': forms.TextInput(attrs={'placeholder': 'Ej. LA1450'}),
            'origen': forms.TextInput(attrs={'placeholder': 'Ej. Quito (UIO)'}),
            'destino': forms.TextInput(attrs={'placeholder': 'Ej. Lima (LIM)'}),
            'precio': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
            'asientos': forms.NumberInput(attrs={'min': '1'}),
        }

    def clean_codigo(self):
        return self.cleaned_data['codigo'].strip().upper()

    def clean_precio(self):
        precio = self.cleaned_data['precio']
        if precio <= 0:
            raise forms.ValidationError('El precio debe ser mayor que cero.')
        return precio

    def clean(self):
        datos = super().clean()
        salida = datos.get('fecha_salida')
        llegada = datos.get('fecha_llegada')
        origen = datos.get('origen')
        destino = datos.get('destino')
        if salida and llegada and llegada <= salida:
            self.add_error('fecha_llegada', 'La llegada debe ser posterior a la salida.')
        if origen and destino and origen.strip().lower() == destino.strip().lower():
            self.add_error('destino', 'El destino debe ser distinto del origen.')
        return datos
