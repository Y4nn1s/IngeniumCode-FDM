from django.urls import path

from . import views


urlpatterns = [
    path('entrenadores/', views.entrenador_list, name='entrenador_list'),
]
