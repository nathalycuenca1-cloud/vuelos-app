from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import Group
from django.shortcuts import redirect, render
from django.utils.http import url_has_allowed_host_and_scheme
from django.views.decorators.http import require_POST

from vuelos.forms.registro_form import RegistroForm


def registro_view(request):
    if request.user.is_authenticated:
        return redirect('inicio')
    if request.method == 'POST':
        form = RegistroForm(request.POST)
        if form.is_valid():
            user = form.save()
            grupo, _ = Group.objects.get_or_create(name='consultores')
            user.groups.add(grupo)
            messages.success(request, 'Cuenta creada exitosamente. Ya puede iniciar sesión.')
            return redirect('login')
    else:
        form = RegistroForm()
    return render(request, 'vuelos/auth/registro.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('inicio')
    siguiente = request.POST.get('next') or request.GET.get('next') or ''
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            messages.success(request, f'Bienvenido, {form.get_user().username}.')
            destino_seguro = url_has_allowed_host_and_scheme(
                siguiente,
                allowed_hosts={request.get_host()},
                require_https=request.is_secure(),
            )
            if siguiente and destino_seguro:
                return redirect(siguiente)
            return redirect(settings.LOGIN_REDIRECT_URL)
    else:
        form = AuthenticationForm(request)
    return render(request, 'vuelos/auth/login.html', {'form': form, 'next': siguiente})


@require_POST
def logout_view(request):
    logout(request)
    messages.info(request, 'Sesión cerrada correctamente.')
    return redirect(settings.LOGOUT_REDIRECT_URL)
