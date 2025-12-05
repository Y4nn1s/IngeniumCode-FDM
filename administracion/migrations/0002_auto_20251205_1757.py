from django.db import migrations
from datetime import datetime

def create_initial_categories(apps, schema_editor):
    Categoria = apps.get_model('administracion', 'Categoria')
    current_year = datetime.now().year
    
    # Categorías FVF (Edades aproximadas para sistema base)
    categories = [
        {'nombre': 'Sub-5', 'min_age': 3, 'max_age': 5},
        {'nombre': 'Sub-7', 'min_age': 6, 'max_age': 7},
        {'nombre': 'Sub-9', 'min_age': 8, 'max_age': 9},
        {'nombre': 'Sub-11', 'min_age': 10, 'max_age': 11},
        {'nombre': 'Sub-13', 'min_age': 12, 'max_age': 13},
        {'nombre': 'Sub-15', 'min_age': 14, 'max_age': 15},
        {'nombre': 'Sub-17', 'min_age': 16, 'max_age': 17},
        {'nombre': 'Sub-19', 'min_age': 18, 'max_age': 19},
    ]

    for cat in categories:
        # Calcular años de nacimiento
        anio_max = current_year - cat['min_age']
        anio_min = current_year - cat['max_age']
        
        # Crear para Masculino, Femenino y Mixto
        for genero in ['MASCULINO', 'FEMENINO', 'MIXTO']:
            nombre_cat = f"{cat['nombre']} {genero.capitalize()}"
            if not Categoria.objects.filter(nombre=nombre_cat).exists():
                Categoria.objects.create(
                    nombre=nombre_cat,
                    anio_nacimiento_min=anio_min,
                    anio_nacimiento_max=anio_max,
                    genero=genero
                )

class Migration(migrations.Migration):

    dependencies = [
        ('administracion', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_initial_categories),
    ]

