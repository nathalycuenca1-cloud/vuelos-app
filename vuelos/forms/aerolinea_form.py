from django import forms

from vuelos.models import Aerolinea


class AerolineaForm(forms.ModelForm):
    class Meta:
        model = Aerolinea
        fields = ['nombre', 'codigo_iata', 'pais', 'activa']
        widgets = {
            'nombre': forms.TextInput(attrs={'placeholder': 'Ej. LATAM Airlines'}),
            'codigo_iata': forms.TextInput(attrs={'placeholder': 'Ej. LA', 'maxlength': 3}),
            'pais': forms.TextInput(attrs={'placeholder': 'Ej. Chile'}),
        }

    def clean_codigo_iata(self):
        codigo = self.cleaned_data['codigo_iata'].strip().upper()
        if not codigo.isalnum() or len(codigo) < 2:
            raise forms.ValidationError('El código IATA debe tener 2 o 3 letras o números.')
        return codigo
