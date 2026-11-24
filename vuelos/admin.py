from django.contrib import admin

from vuelos.models import Aerolinea, Pasajero, Reserva, Vuelo


@admin.register(Aerolinea)
class AerolineaAdmin(admin.ModelAdmin):
    list_display = ('nombre', 'codigo_iata', 'pais', 'activa')
    list_filter = ('activa', 'pais')
    search_fields = ('nombre', 'codigo_iata', 'pais')


@admin.register(Vuelo)
class VueloAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'aerolinea', 'origen', 'destino', 'fecha_salida', 'precio', 'estado')
    list_filter = ('estado', 'aerolinea', 'fecha_salida')
    search_fields = ('codigo', 'origen', 'destino', 'aerolinea__nombre')


@admin.register(Pasajero)
class PasajeroAdmin(admin.ModelAdmin):
    list_display = ('apellidos', 'nombres', 'documento', 'email', 'nacionalidad')
    list_filter = ('nacionalidad',)
    search_fields = ('nombres', 'apellidos', 'documento', 'email')


@admin.register(Reserva)
class ReservaAdmin(admin.ModelAdmin):
    list_display = ('codigo', 'vuelo', 'clase', 'estado', 'fecha_reserva', 'total', 'creado_por')
    list_filter = ('estado', 'clase', 'fecha_reserva')
    search_fields = ('codigo', 'vuelo__codigo', 'pasajeros__apellidos', 'pasajeros__documento')
    filter_horizontal = ('pasajeros',)
