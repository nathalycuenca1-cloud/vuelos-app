from django.contrib import messages
from django.contrib.auth.decorators import login_required, permission_required
from django.db.models import ProtectedError
from django.shortcuts import get_object_or_404, redirect, render

from vuelos.forms.aerolinea_form import AerolineaForm
from vuelos.models import Aerolinea


@login_required
@permission_required('vuelos.view_aerolinea', raise_exception=True)
def aerolinea_list(request):
    aerolineas = Aerolinea.objects.all()
    return render(request, 'vuelos/aerolineas/aerolinea_list.html', {'aerolineas': aerolineas})


@login_required
@permission_required('vuelos.view_aerolinea', raise_exception=True)
def aerolinea_detail(request, pk):
    aerolinea = get_object_or_404(Aerolinea, pk=pk)
    vuelos = aerolinea.vuelos.all()
    return render(request, 'vuelos/aerolineas/aerolinea_detail.html', {'aerolinea': aerolinea, 'vuelos': vuelos})


@login_required
@permission_required('vuelos.add_aerolinea', raise_exception=True)
def aerolinea_create(request):
    if request.method == 'POST':
        form = AerolineaForm(request.POST)
        if form.is_valid():
            aerolinea = form.save()
            messages.success(request, 'Aerolínea creada exitosamente.')
            return redirect(aerolinea)
    else:
        form = AerolineaForm()
    return render(request, 'vuelos/aerolineas/formulario.html', {'form': form, 'titulo': 'Nueva aerolínea'})


@login_required
@permission_required('vuelos.change_aerolinea', raise_exception=True)
def aerolinea_update(request, pk):
    aerolinea = get_object_or_404(Aerolinea, pk=pk)
    if request.method == 'POST':
        form = AerolineaForm(request.POST, instance=aerolinea)
        if form.is_valid():
            form.save()
            messages.success(request, 'Aerolínea actualizada exitosamente.')
            return redirect(aerolinea)
    else:
        form = AerolineaForm(instance=aerolinea)
    return render(request, 'vuelos/aerolineas/formulario.html', {'form': form, 'titulo': 'Editar aerolínea'})


@login_required
@permission_required('vuelos.delete_aerolinea', raise_exception=True)
def aerolinea_delete(request, pk):
    aerolinea = get_object_or_404(Aerolinea, pk=pk)
    if request.method == 'POST':
        try:
            aerolinea.delete()
        except ProtectedError:
            messages.error(request, 'No se puede eliminar: la aerolínea tiene vuelos asociados.')
            return redirect(aerolinea)
        messages.success(request, 'Aerolínea eliminada exitosamente.')
        return redirect('aerolinea_list')
    return render(request, 'vuelos/aerolineas/confirmar_eliminar.html', {'aerolinea': aerolinea})
