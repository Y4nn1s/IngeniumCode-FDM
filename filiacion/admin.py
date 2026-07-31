from django.contrib import admin
from .models import Atleta, Representante, CAT_Posicion, CAT_Lateralidad


admin.site.register(CAT_Posicion)
admin.site.register(CAT_Lateralidad)


@admin.register(Atleta)
class AtletaAdmin(admin.ModelAdmin):
    list_display = (
        'nombres', 'apellidos', 'cedula_identidad',
        'categoria', 'posicion', 'lateralidad',
        'es_condicion_especial', 'activo', 'becado',
    )
    search_fields = (
        'nombres', 'apellidos',
        'cedula_identidad', 'numero_acta_nacimiento',
    )
    list_filter = (
        'es_condicion_especial', 'activo', 'becado',
        'categoria', 'posicion', 'lateralidad',
    )
    readonly_fields = ('cedula_identidad',)
    fieldsets = (
        ('Identificación', {
            'fields': (
                'representante', 'categoria',
                'nombres', 'apellidos', 'fecha_nacimiento',
                'numero_acta_nacimiento', 'cedula_identidad',
            )
        }),
        ('Deportivo', {
            'fields': ('posicion', 'lateralidad', 'peso_kg', 'altura_mts', 'foto_perfil'),
        }),
        ('Estado y Condición Médica', {
            'fields': ('activo', 'becado', 'es_condicion_especial', 'observacion_medica'),
        }),
    )


@admin.register(Representante)
class RepresentanteAdmin(admin.ModelAdmin):
    list_display = (
        'nombres', 'apellidos', 'cedula_identidad',
        'telefono_principal', 'correo_electronico',
        'usuario', 'telegram_chat_id',
    )
    search_fields = ('nombres', 'apellidos', 'cedula_identidad', 'correo_electronico')
    list_filter = ('usuario',)
    raw_id_fields = ('usuario',)
