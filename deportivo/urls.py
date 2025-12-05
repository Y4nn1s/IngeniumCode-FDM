from django.urls import path
from . import views

urlpatterns = [
    path('partidos/', views.partido_list, name='partido_list'),
    path('partidos/programar/', views.partido_create, name='partido_create'),
    path('partidos/<int:pk>/resultado/', views.partido_registrar_resultado, name='partido_resultado'),
]
