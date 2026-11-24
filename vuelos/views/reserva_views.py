from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render

from vuelos.forms.reserva_form import ReservaForm
from vuelos.models import Reserva
from vuelos.permisos import puede_modificar


@login_required
@permission_required('vuelos.view_reserva', raise_exception=True)
def reserva_list(request):
    reservas = Reserva.objects.select_related('vuelo', 'creado_por')
    return render(request, 'vuelos/reservas/reserva_list.html', {'reservas': reservas})


@login_required
@permission_required('vuelos.view_reserva', raise_exception=True)
def reserva_detail(request, pk):
    reserva = get_object_or_404(Reserva.objects.select_related('vuelo', 'creado_por'), pk=pk)
    pasajeros = reserva.pasajeros.all()
    return render(request, 'vuelos/reservas/reserva_detail.html', {'reserva': reserva, 'pasajeros': pasajeros})


@login_required
@permission_required('vuelos.add_reserva', raise_exception=True)
def reserva_create(request):
    if request.method == 'POST':
        form = ReservaForm(request.POST)
        if form.is_valid():
            reserva = form.save(commit=False)
            reserva.creado_por = request.user
            reserva.save()
            form.save_m2m()
            messages.success(request, 'Reserva creada exitosamente.')
            return redirect(reserva)
    else:
        form = ReservaForm()
    return render(request, 'vuelos/reservas/formulario.html', {'form': form, 'titulo': 'Nueva reserva'})


@login_required
@permission_required('vuelos.change_reserva', raise_exception=True)
def reserva_update(request, pk):
    reserva = get_object_or_404(Reserva, pk=pk)
    if not puede_modificar(request.user, reserva):
        raise PermissionDenied
    if request.method == 'POST':
        form = ReservaForm(request.POST, instance=reserva)
        if form.is_valid():
            form.save()
            messages.success(request, 'Reserva actualizada exitosamente.')
            return redirect(reserva)
    else:
        form = ReservaForm(instance=reserva)
    return render(request, 'vuelos/reservas/formulario.html', {'form': form, 'titulo': 'Editar reserva'})


@login_required
@permission_required('vuelos.delete_reserva', raise_exception=True)
def reserva_delete(request, pk):
    reserva = get_object_or_404(Reserva, pk=pk)
    if not puede_modificar(request.user, reserva):
        raise PermissionDenied
    if request.method == 'POST':
        reserva.delete()
        messages.success(request, 'Reserva eliminada exitosamente.')
        return redirect('reserva_list')
    return render(request, 'vuelos/reservas/confirmar_eliminar.html', {'reserva': reserva})
