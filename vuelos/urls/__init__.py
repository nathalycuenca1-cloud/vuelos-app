from django.urls import path

from vuelos import views
from vuelos.urls.aerolinea_urls import urlpatterns as aerolinea_urlpatterns
from vuelos.urls.vuelo_urls import urlpatterns as vuelo_urlpatterns
from vuelos.urls.pasajero_urls import urlpatterns as pasajero_urlpatterns
from vuelos.urls.reserva_urls import urlpatterns as reserva_urlpatterns
from vuelos.urls.auth_urls import urlpatterns as auth_urlpatterns

urlpatterns = [path('', views.inicio, name='inicio')]
urlpatterns += aerolinea_urlpatterns
urlpatterns += vuelo_urlpatterns
urlpatterns += pasajero_urlpatterns
urlpatterns += reserva_urlpatterns
urlpatterns += auth_urlpatterns
