# finanzas/urls.py
from django.urls import path
from . import views

app_name = 'finanzas'

urlpatterns = [
    path('reportar/', views.reportar_pago, name='reportar'),
    path('mis-pagos/', views.mis_pagos, name='mis_pagos'),

    path('admin/bandeja/', views.bandeja_admin, name='bandeja'),
    path('admin/<int:pk>/', views.detalle_admin, name='detalle'),
    path('admin/<int:pk>/aprobar/', views.aprobar, name='aprobar'),
    path('admin/<int:pk>/rechazar/', views.rechazar, name='rechazar'),

    path('telegram/webhook/', views.telegram_webhook, name='telegram_webhook'),
    path('comprobante/<int:pago_id>/', views.descargar_comprobante, name='comprobante'),
]
