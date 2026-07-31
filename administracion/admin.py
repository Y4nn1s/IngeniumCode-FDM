from django.contrib import admin
from .models import (
    # Modelos legados (se mantienen intactos - DATA LOSS PREVENTION)
    CAT_Cargo, CAT_Licencia, CAT_Genero,
    Personal, Categoria, CategoriaEntrenadores,
    # Nuevos modelos Fase 2 (referencian catálogos de core)
    Personal2, Categoria2, CategoriaEntrenadores2,
)


# ==============================================================================
# ADMIN - Modelos LEGADOS (sin modificar, registrados con admin.site.register)
# ==============================================================================

admin.site.register(CAT_Cargo)
admin.site.register(CAT_Licencia)
admin.site.register(CAT_Genero)
admin.site.register(Personal)
admin.site.register(Categoria)
admin.site.register(CategoriaEntrenadores)


@admin.register(Personal2)
class Personal2Admin(admin.ModelAdmin):
    list_display = ('cedula_identidad', 'nombres', 'apellidos', 'cargo', 'licencia', 'activo')
    search_fields = ('cedula_identidad', 'nombres', 'apellidos')
    list_filter = ('activo', 'cargo')
    ordering = ('apellidos', 'nombres')


@admin.register(Categoria2)
class Categoria2Admin(admin.ModelAdmin):
    list_display = ('nombre', 'genero', 'coordinador_supervisor', 'delegado', 'anio_nacimiento_min', 'anio_nacimiento_max')
    search_fields = ('nombre',)
    list_filter = ('genero',)
    ordering = ('nombre',)


@admin.register(CategoriaEntrenadores2)
class CategoriaEntrenadores2Admin(admin.ModelAdmin):
    list_display = ('categoria', 'personal')
    search_fields = ('categoria__nombre', 'personal__nombres', 'personal__apellidos')
    list_filter = ('categoria',)
