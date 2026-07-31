from django.contrib import admin
from .models import Personal, Categoria, CategoriaEntrenadores


@admin.register(Personal)
class PersonalAdmin(admin.ModelAdmin):
    list_display = ('cedula_identidad', 'nombres', 'apellidos', 'cargo', 'licencia', 'activo')
    search_fields = ('cedula_identidad', 'nombres', 'apellidos')
    list_filter = ('activo', 'cargo')
    ordering = ('apellidos', 'nombres')


@admin.register(Categoria)
class CategoriaAdmin(admin.ModelAdmin):
    list_display = (
        'nombre', 'genero', 'coordinador_supervisor',
        'delegado', 'anio_nacimiento_min', 'anio_nacimiento_max',
    )
    search_fields = ('nombre',)
    list_filter = ('genero',)
    ordering = ('nombre',)


@admin.register(CategoriaEntrenadores)
class CategoriaEntrenadoresAdmin(admin.ModelAdmin):
    list_display = ('categoria', 'personal')
    search_fields = ('categoria__nombre', 'personal__nombres', 'personal__apellidos')
    list_filter = ('categoria',)
