from django.urls import path

from . import views


urlpatterns = [
    path('entrenadores/', views.entrenador_list, name='entrenador_list'),
    path('entrenadores/nuevo/', views.EntrenadorCreateView.as_view(), name='entrenador_create'),
    path('entrenadores/<int:pk>/editar/', views.EntrenadorUpdateView.as_view(), name='entrenador_update'),
    path('entrenadores/<int:pk>/eliminar/', views.EntrenadorDeleteView.as_view(), name='entrenador_delete'),
]

