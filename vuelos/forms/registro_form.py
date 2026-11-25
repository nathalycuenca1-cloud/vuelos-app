from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.db import transaction
from django.utils import timezone

from vuelos.models import Pasajero


class RegistroForm(UserCreationForm):
    email = forms.EmailField(required=True, label='Correo electrónico')
    nombres = forms.CharField(max_length=80, label='Nombres')
    apellidos = forms.CharField(max_length=80, label='Apellidos')
    documento = forms.CharField(max_length=20, label='Cédula o pasaporte')
    fecha_nacimiento = forms.DateField(
        label='Fecha de nacimiento',
        widget=forms.DateInput(attrs={'type': 'date'}, format='%Y-%m-%d'),
    )

    field_order = [
        'username', 'email', 'nombres', 'apellidos', 'documento',
        'fecha_nacimiento', 'password1', 'password2',
    ]

    class Meta(UserCreationForm.Meta):
        model = User
        fields = ['username', 'email']

    def clean_email(self):
        email = self.cleaned_data['email'].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('Ya existe un usuario con este correo.')
        return email

    def clean_documento(self):
        documento = self.cleaned_data['documento'].strip().upper()
        if len(documento) < 5:
            raise forms.ValidationError('El documento debe tener al menos 5 caracteres.')
        if Pasajero.objects.filter(documento=documento).exists():
            raise forms.ValidationError('Ya existe un pasajero con este documento.')
        return documento

    def clean_fecha_nacimiento(self):
        fecha = self.cleaned_data['fecha_nacimiento']
        if fecha > timezone.localdate():
            raise forms.ValidationError('La fecha de nacimiento no puede ser futura.')
        return fecha

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            with transaction.atomic():
                user.save()
                Pasajero.objects.create(
                    nombres=self.cleaned_data['nombres'],
                    apellidos=self.cleaned_data['apellidos'],
                    documento=self.cleaned_data['documento'],
                    email=user.email,
                    fecha_nacimiento=self.cleaned_data['fecha_nacimiento'],
                    creado_por=user,
                )
        return user