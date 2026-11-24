from django import forms
from django.utils import timezone

from vuelos.models import Pasajero


class PasajeroForm(forms.ModelForm):
    class Meta:
        model = Pasajero
        fields = ['nombres', 'apellidos', 'documento', 'email', 'fecha_nacimiento', 'nacionalidad']
        widgets = {
            'nombres': forms.TextInput(attrs={'placeholder': 'Nombres'}),
            'apellidos': forms.TextInput(attrs={'placeholder': 'Apellidos'}),
            'documento': forms.TextInput(attrs={'placeholder': 'Cédula o pasaporte'}),
            'email': forms.EmailInput(attrs={'placeholder': 'correo@ejemplo.com'}),
            'fecha_nacimiento': forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
        }

    def clean_documento(self):
        documento = self.cleaned_data['documento'].strip().upper()
        if len(documento) < 5:
            raise forms.ValidationError('El documento debe tener al menos 5 caracteres.')
        return documento

    def clean_fecha_nacimiento(self):
        fecha = self.cleaned_data['fecha_nacimiento']
        if fecha > timezone.localdate():
            raise forms.ValidationError('La fecha de nacimiento no puede ser futura.')
        return fecha
