from django.contrib import admin
from .models import Atleta, Representante

@admin.register(Atleta)
class AtletaAdmin(admin.ModelAdmin):
    list_display = ('nombres', 'apellidos', 'categoria', 'activo')
    search_fields = ('nombres', 'apellidos', 'cedula_escolar')
    list_filter = ('categoria', 'activo')

@admin.register(Representante)
class RepresentanteAdmin(admin.ModelAdmin):
    list_display = ('nombres', 'apellidos', 'cedula_identidad', 'telefono_principal', 'usuario', 'telegram_chat_id')
    search_fields = ('nombres', 'apellidos', 'cedula_identidad')
    list_filter = ('usuario',)
    raw_id_fields = ('usuario',)
