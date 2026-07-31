from django.contrib import admin
from .models import (
    Partido, Estadistica,
    CAT_TipoPartido, CAT_CondicionPartido,
    EvaluacionTecnica, EvaluacionPsicosocial,
)

admin.site.register(CAT_TipoPartido)
admin.site.register(CAT_CondicionPartido)
admin.site.register(Estadistica)
admin.site.register(EvaluacionTecnica)
admin.site.register(EvaluacionPsicosocial)


@admin.register(Partido)
class PartidoAdmin(admin.ModelAdmin):
    list_display = (
        '__str__', 'categoria',
        'tipo', 'condicion',
        'tipo_legacy', 'condicion_legacy',
        'goles_favor_escuela', 'goles_contra_rival',
        'resultado',
        'procesado',
    )
    list_filter = (
        'tipo', 'condicion',
        'tipo_legacy', 'condicion_legacy',
        'procesado',
    )
    search_fields = ('equipo_rival',)
    date_hierarchy = 'fecha_hora'
    ordering = ('-fecha_hora',)
