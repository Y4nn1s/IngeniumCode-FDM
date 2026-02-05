from django.urls import path
from . import views

urlpatterns = [
    # Atletas
    path('atletas/', views.atleta_list, name='atleta_list'),
    path('atletas/crear/', views.atleta_create, name='atleta_create'),
    path('atletas/<int:pk>/', views.atleta_detail, name='atleta_detail'),
    path('atletas/<int:pk>/editar/', views.atleta_update, name='atleta_update'),
    path('atletas/<int:pk>/eliminar/', views.atleta_delete, name='atleta_delete'),

    # Representantes
    path('representantes/', views.representante_list, name='representante_list'),
    path('representantes/crear/', views.representante_create, name='representante_create'),
    path('representantes/<int:pk>/', views.representante_detail, name='representante_detail'),
    path('representantes/<int:pk>/editar/', views.representante_update, name='representante_update'),
]
