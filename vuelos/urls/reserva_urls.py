from django.urls import path

from vuelos import views

urlpatterns = [
    path('reservas/', views.reserva_list, name='reserva_list'),
    path('reservas/nuevo/', views.reserva_create, name='reserva_create'),
    path('reservas/<int:pk>/', views.reserva_detail, name='reserva_detail'),
    path('reservas/<int:pk>/editar/', views.reserva_update, name='reserva_update'),
    path('reservas/<int:pk>/eliminar/', views.reserva_delete, name='reserva_delete'),
]
