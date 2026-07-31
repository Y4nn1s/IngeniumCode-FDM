from django.contrib import admin
from .models import (
    Pago, PagoAuditLog, Mensualidad,
    Patrocinante, Aporte, TasaBCV,
    CAT_Banco, CAT_EstadoPago, CAT_MetodoPago,
)

# Catálogos locales (legados - se conservan)
admin.site.register(CAT_Banco)
admin.site.register(CAT_EstadoPago)
admin.site.register(CAT_MetodoPago)


class PagoAuditLogInline(admin.TabularInline):
    model = PagoAuditLog
    extra = 0
    readonly_fields = ('timestamp', 'accion', 'estado_anterior', 'estado_nuevo', 'actor', 'detalles')
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'representante', 'concepto',
        'metodo', 'banco_emisor', 'estado',     # Nuevas FK → core
        'monto_bs', 'monto_usd', 'tasa_bcv',
        'fecha_pago', 'fecha_reporte',
    )
    list_filter = (
        'estado', 'metodo', 'banco_emisor',     # Nuevas FK → core
        'estado_legacy', 'metodo_legacy', 'banco_emisor_legacy',  # Legados
        'fecha_pago',
    )
    search_fields = (
        'representante__cedula_identidad',
        'representante__nombres',
        'representante__apellidos',
        'referencia',
        'concepto',
    )
    readonly_fields = (
        'comprobante_hash', 'fecha_reporte',
        'revisado_por', 'revisado_en', 'monto_usd',
    )
    ordering = ('-fecha_reporte',)
    date_hierarchy = 'fecha_pago'
    inlines = [PagoAuditLogInline]
    fieldsets = (
        ('Datos del Pago', {
            'fields': (
                'representante', 'concepto',
                'metodo', 'banco_emisor', 'referencia',
                'fecha_pago',
            )
        }),
        ('Montos', {
            'fields': ('monto_bs', 'tasa_bcv', 'monto_usd'),
        }),
        ('Estado y Comprobante', {
            'fields': ('estado', 'comprobante', 'comprobante_hash', 'motivo_rechazo'),
        }),
        ('Revisión', {
            'fields': ('revisado_por', 'revisado_en', 'fecha_reporte'),
        }),
        ('Campos Legados (no usar)', {
            'fields': ('metodo_legacy', 'banco_emisor_legacy', 'estado_legacy'),
            'classes': ('collapse',),
            'description': 'Campos del catálogo local anterior. Conservados para preservación de datos.',
        }),
    )


@admin.register(Mensualidad)
class MensualidadAdmin(admin.ModelAdmin):
    list_display = (
        'atleta', 'periodo_mes', 'periodo_anio',
        'monto_usd', 'fecha_vencimiento',
        'esta_pagada', 'vencida',
    )
    list_filter = ('periodo_anio', 'periodo_mes')
    search_fields = (
        'atleta__nombres', 'atleta__apellidos',
        'atleta__cedula_identidad',
    )
    date_hierarchy = 'fecha_vencimiento'


@admin.register(PagoAuditLog)
class PagoAuditLogAdmin(admin.ModelAdmin):
    """Registro de auditoría: solo lectura total (Event Sourcing)."""
    list_display = ('timestamp', 'pago', 'accion', 'estado_anterior', 'estado_nuevo', 'actor')
    list_filter = ('accion', 'timestamp')
    search_fields = ('pago__id', 'actor__username', 'accion')
    readonly_fields = (
        'pago', 'accion', 'estado_anterior', 'estado_nuevo',
        'actor', 'detalles', 'timestamp',
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Patrocinante)
class PatrocinanteAdmin(admin.ModelAdmin):
    list_display = ('nombre_empresa', 'tipo_ente', 'persona_contacto')
    search_fields = ('nombre_empresa',)


@admin.register(Aporte)
class AporteAdmin(admin.ModelAdmin):
    list_display = ('patrocinante', 'fecha_aporte', 'tipo', 'valor_estimado_usd')
    list_filter = ('tipo', 'fecha_aporte')


@admin.register(TasaBCV)
class TasaBCVAdmin(admin.ModelAdmin):
    list_display = ('fecha', 'tasa', 'fuente', 'capturada_en')
    list_filter = ('fuente',)
    date_hierarchy = 'fecha'
    ordering = ('-fecha',)
