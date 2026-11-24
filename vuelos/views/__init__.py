from vuelos.views.inicio_views import inicio
from vuelos.views.auth_views import registro_view, login_view, logout_view
from vuelos.views.aerolinea_views import (
    aerolinea_list, aerolinea_detail, aerolinea_create, aerolinea_update, aerolinea_delete,
)
from vuelos.views.vuelo_views import (
    vuelo_list, vuelo_detail, vuelo_create, vuelo_update, vuelo_delete,
)
from vuelos.views.pasajero_views import (
    pasajero_list, pasajero_detail, pasajero_create, pasajero_update, pasajero_delete,
)
from vuelos.views.reserva_views import (
    reserva_list, reserva_detail, reserva_create, reserva_update, reserva_delete,
)
