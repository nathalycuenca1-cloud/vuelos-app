from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import ProtectedError
from django.shortcuts import get_object_or_404, redirect, render

from vuelos.forms.vuelo_form import VueloForm
from vuelos.models import Vuelo


@login_required
@permission_required('vuelos.view_vuelo', raise_exception=True)
def vuelo_list(request):
    vuelos = Vuelo.objects.select_related('aerolinea')
    return render(request, 'vuelos/vuelos/vuelo_list.html', {'vuelos': vuelos})


@login_required
@permission_required('vuelos.view_vuelo', raise_exception=True)
def vuelo_detail(request, pk):
    vuelo = get_object_or_404(Vuelo.objects.select_related('aerolinea'), pk=pk)
    reservas = vuelo.reservas.all()
    return render(request, 'vuelos/vuelos/vuelo_detail.html', {'vuelo': vuelo, 'reservas': reservas})


@login_required
@permission_required('vuelos.add_vuelo', raise_exception=True)
def vuelo_create(request):
    if request.method == 'POST':
        form = VueloForm(request.POST)
        if form.is_valid():
            vuelo = form.save()
            messages.success(request, 'Vuelo creado exitosamente.')
            return redirect(vuelo)
    else:
        form = VueloForm()
    return render(request, 'vuelos/vuelos/formulario.html', {'form': form, 'titulo': 'Nuevo vuelo'})


@login_required
@permission_required('vuelos.change_vuelo', raise_exception=True)
def vuelo_update(request, pk):
    vuelo = get_object_or_404(Vuelo, pk=pk)
    if request.method == 'POST':
        form = VueloForm(request.POST, instance=vuelo)
        if form.is_valid():
            form.save()
            messages.success(request, 'Vuelo actualizado exitosamente.')
            return redirect(vuelo)
    else:
        form = VueloForm(instance=vuelo)
    return render(request, 'vuelos/vuelos/formulario.html', {'form': form, 'titulo': 'Editar vuelo'})


@login_required
@permission_required('vuelos.delete_vuelo', raise_exception=True)
def vuelo_delete(request, pk):
    vuelo = get_object_or_404(Vuelo, pk=pk)
    if request.method == 'POST':
        try:
            vuelo.delete()
        except ProtectedError:
            messages.error(request, 'No se puede eliminar: el vuelo tiene reservas asociadas.')
            return redirect(vuelo)
        messages.success(request, 'Vuelo eliminado exitosamente.')
        return redirect('vuelo_list')
    return render(request, 'vuelos/vuelos/confirmar_eliminar.html', {'vuelo': vuelo})
