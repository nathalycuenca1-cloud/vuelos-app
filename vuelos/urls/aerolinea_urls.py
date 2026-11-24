from django.urls import path

from vuelos import views

urlpatterns = [
    path('aerolineas/', views.aerolinea_list, name='aerolinea_list'),
    path('aerolineas/nuevo/', views.aerolinea_create, name='aerolinea_create'),
    path('aerolineas/<int:pk>/', views.aerolinea_detail, name='aerolinea_detail'),
    path('aerolineas/<int:pk>/editar/', views.aerolinea_update, name='aerolinea_update'),
    path('aerolineas/<int:pk>/eliminar/', views.aerolinea_delete, name='aerolinea_delete'),
]
