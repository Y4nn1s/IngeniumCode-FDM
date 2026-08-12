from django.contrib import admin
from .models import (
    Partido, Estadistica,
    EvaluacionTecnica, EvaluacionPsicosocial,
)

admin.site.register(Estadistica)
admin.site.register(EvaluacionTecnica)
admin.site.register(EvaluacionPsicosocial)


@admin.register(Partido)
class PartidoAdmin(admin.ModelAdmin):
    list_display = (
        '__str__', 'categoria',
        'tipo', 'condicion', 'estado',
        'goles_favor_escuela', 'goles_contra_rival',
        'resultado',
    )
    list_filter = (
        'tipo', 'condicion', 'estado',
    )
    search_fields = ('equipo_rival',)
    date_hierarchy = 'fecha_hora'
    ordering = ('-fecha_hora',)
