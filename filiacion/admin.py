from django.contrib import admin
from .models import Atleta, Representante, CAT_Posicion, CAT_Lateralidad

admin.site.register(CAT_Posicion)
admin.site.register(CAT_Lateralidad)

@admin.register(Atleta)
class AtletaAdmin(admin.ModelAdmin):
    list_display = ('nombres', 'apellidos', 'categoria', 'cedula_identidad', 'activo')
    search_fields = ('nombres', 'apellidos', 'cedula_identidad', 'numero_acta_nacimiento')
    list_filter = ('categoria', 'activo', 'posicion', 'lateralidad')

@admin.register(Representante)
class RepresentanteAdmin(admin.ModelAdmin):
    list_display = ('nombres', 'apellidos', 'cedula_identidad', 'telefono_principal', 'usuario', 'telegram_chat_id')
    search_fields = ('nombres', 'apellidos', 'cedula_identidad')
    list_filter = ('usuario',)
    raw_id_fields = ('usuario',)
