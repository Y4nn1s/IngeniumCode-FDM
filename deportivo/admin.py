from django.contrib import admin
from .models import (
    Partido, Estadistica,
    CAT_TipoPartido, CAT_CondicionPartido,
    EvaluacionTecnica, EvaluacionPsicosocial,
)

# Catálogos locales (legados - se conservan)
admin.site.register(CAT_TipoPartido)
admin.site.register(CAT_CondicionPartido)
admin.site.register(Estadistica)
admin.site.register(EvaluacionTecnica)
admin.site.register(EvaluacionPsicosocial)


@admin.register(Partido)
class PartidoAdmin(admin.ModelAdmin):
    list_display = (
        '__str__', 'categoria',
        'tipo', 'condicion',          # FK nuevas → core
        'tipo_legacy', 'condicion_legacy',  # FK viejas → catálogos locales
        'goles_favor_escuela', 'goles_contra_rival',
        'resultado',                   # Propiedad calculada (no campo de BD)
        'procesado',
    )
    list_filter = (
        'tipo', 'condicion',          # Nuevas FK
        'tipo_legacy', 'condicion_legacy',  # Legados
        'procesado',
    )
    search_fields = ('equipo_rival',)
    date_hierarchy = 'fecha_hora'
    ordering = ('-fecha_hora',)
