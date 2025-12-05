from django.contrib import admin
from .models import Partido, Estadistica

@admin.register(Partido)
class PartidoAdmin(admin.ModelAdmin):
    list_display = ('__str__', 'tipo', 'resultado', 'procesado')
    list_filter = ('tipo', 'procesado')

admin.site.register(Estadistica)
