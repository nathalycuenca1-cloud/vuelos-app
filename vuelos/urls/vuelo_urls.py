from django.urls import path

from vuelos import views

urlpatterns = [
    path('vuelos/', views.vuelo_list, name='vuelo_list'),
    path('vuelos/nuevo/', views.vuelo_create, name='vuelo_create'),
    path('vuelos/<int:pk>/', views.vuelo_detail, name='vuelo_detail'),
    path('vuelos/<int:pk>/editar/', views.vuelo_update, name='vuelo_update'),
    path('vuelos/<int:pk>/eliminar/', views.vuelo_delete, name='vuelo_delete'),
]
