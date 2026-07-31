from django.contrib import admin
from .models import (
    CAT_Cargo, CAT_Licencia, CAT_Genero,
    Personal, Categoria, CategoriaEntrenadores
)

admin.site.register(CAT_Cargo)
admin.site.register(CAT_Licencia)
admin.site.register(CAT_Genero)
admin.site.register(Personal)
admin.site.register(Categoria)
admin.site.register(CategoriaEntrenadores)
