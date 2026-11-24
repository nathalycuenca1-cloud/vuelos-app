from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.shortcuts import get_object_or_404, redirect, render

from vuelos.forms.pasajero_form import PasajeroForm
from vuelos.models import Pasajero


@login_required
@permission_required('vuelos.view_pasajero', raise_exception=True)
def pasajero_list(request):
    pasajeros = Pasajero.objects.all()
    return render(request, 'vuelos/pasajeros/pasajero_list.html', {'pasajeros': pasajeros})


@login_required
@permission_required('vuelos.view_pasajero', raise_exception=True)
def pasajero_detail(request, pk):
    pasajero = get_object_or_404(Pasajero, pk=pk)
    reservas = pasajero.reservas.select_related('vuelo')
    return render(request, 'vuelos/pasajeros/pasajero_detail.html', {'pasajero': pasajero, 'reservas': reservas})


@login_required
@permission_required('vuelos.add_pasajero', raise_exception=True)
def pasajero_create(request):
    if request.method == 'POST':
        form = PasajeroForm(request.POST)
        if form.is_valid():
            pasajero = form.save()
            messages.success(request, 'Pasajero creado exitosamente.')
            return redirect(pasajero)
    else:
        form = PasajeroForm()
    return render(request, 'vuelos/pasajeros/formulario.html', {'form': form, 'titulo': 'Nuevo pasajero'})


@login_required
@permission_required('vuelos.change_pasajero', raise_exception=True)
def pasajero_update(request, pk):
    pasajero = get_object_or_404(Pasajero, pk=pk)
    if request.method == 'POST':
        form = PasajeroForm(request.POST, instance=pasajero)
        if form.is_valid():
            form.save()
            messages.success(request, 'Pasajero actualizado exitosamente.')
            return redirect(pasajero)
    else:
        form = PasajeroForm(instance=pasajero)
    return render(request, 'vuelos/pasajeros/formulario.html', {'form': form, 'titulo': 'Editar pasajero'})


@login_required
@permission_required('vuelos.delete_pasajero', raise_exception=True)
def pasajero_delete(request, pk):
    pasajero = get_object_or_404(Pasajero, pk=pk)
    if request.method == 'POST':
        pasajero.delete()
        messages.success(request, 'Pasajero eliminado exitosamente.')
        return redirect('pasajero_list')
    return render(request, 'vuelos/pasajeros/confirmar_eliminar.html', {'pasajero': pasajero})
