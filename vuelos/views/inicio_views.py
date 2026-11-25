from django.shortcuts import render

from vuelos.models import Aerolinea, Pasajero, Reserva, Vuelo


def inicio(request):
    contexto = {
        'total_aerolineas': Aerolinea.objects.count(),
        'total_vuelos': Vuelo.objects.count(),
        'total_pasajeros': Pasajero.objects.count(),
        'total_reservas': Reserva.objects.count(),
        'vuelos_destacados': Vuelo.objects.select_related('aerolinea').filter(estado=Vuelo.Estado.PROGRAMADO)[:6],
    }
    return render(request, 'vuelos/inicio.html', contexto)