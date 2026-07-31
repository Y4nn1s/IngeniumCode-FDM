from django.contrib import admin
from .models import (
    Partido, Estadistica, CAT_TipoPartido, CAT_CondicionPartido,
    EvaluacionTecnica, EvaluacionPsicosocial
)

admin.site.register(CAT_TipoPartido)
admin.site.register(CAT_CondicionPartido)
admin.site.register(Estadistica)
admin.site.register(EvaluacionTecnica)
admin.site.register(EvaluacionPsicosocial)

@admin.register(Partido)
class PartidoAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'tipo', 'condicion', 'resultado', 'procesado')
    list_filter = ('tipo', 'condicion', 'procesado')
