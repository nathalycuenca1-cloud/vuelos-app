from django.urls import path

from vuelos import views

urlpatterns = [
    path('pasajeros/', views.pasajero_list, name='pasajero_list'),
    path('pasajeros/nuevo/', views.pasajero_create, name='pasajero_create'),
    path('pasajeros/<int:pk>/', views.pasajero_detail, name='pasajero_detail'),
    path('pasajeros/<int:pk>/editar/', views.pasajero_update, name='pasajero_update'),
    path('pasajeros/<int:pk>/eliminar/', views.pasajero_delete, name='pasajero_delete'),
]
