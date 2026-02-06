from django.urls import path
from . import views


urlpatterns = [
    # Partidos
    path('partidos/', views.partido_list, name='partido_list'),
    path('partidos/programar/', views.partido_create, name='partido_create'),
    path(
        'partidos/<int:pk>/resultado/',
        views.partido_registrar_resultado,
        name='partido_resultado'
    ),
    path(
        'partidos/<int:pk>/',
        views.partido_detail,
        name='partido_detail'
    ),
    # Evaluación Técnica
    path(
        'evaluacion-tecnica/nueva/',
        views.EvaluacionTecnicaCreateView.as_view(),
        name='evaluacion_tecnica_create'
    ),
    path(
        'evaluacion-tecnica/<int:pk>/editar/',
        views.EvaluacionTecnicaUpdateView.as_view(),
        name='evaluacion_tecnica_update'
    ),
    # Evaluación Psicosocial
    path(
        'evaluacion-psicosocial/nueva/',
        views.EvaluacionPsicosocialCreateView.as_view(),
        name='evaluacion_psicosocial_create'
    ),
    path(
        'evaluacion-psicosocial/<int:pk>/editar/',
        views.EvaluacionPsicosocialUpdateView.as_view(),
        name='evaluacion_psicosocial_update'
    ),
]
