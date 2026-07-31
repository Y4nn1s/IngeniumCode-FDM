from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()


# === Catálogos Base (3NF) ===

class CAT_Cargo(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Catálogo - Cargo'
        verbose_name_plural = 'Catálogos - Cargos'

    def __str__(self):
        return self.nombre


class CAT_Licencia(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    descripcion = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Catálogo - Licencia'
        verbose_name_plural = 'Catálogos - Licencias'

    def __str__(self):
        return self.nombre


class CAT_Genero(models.Model):
    nombre = models.CharField(max_length=20, unique=True)

    class Meta:
        verbose_name = 'Catálogo - Género Categoria'
        verbose_name_plural = 'Catálogos - Géneros Categoría'

    def __str__(self):
        return self.nombre


# === Modelos de Negocio ===

class Personal(models.Model):
    usuario = models.OneToOneField(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='perfil_personal'
    )
    cargo = models.ForeignKey(CAT_Cargo, on_delete=models.PROTECT, related_name='personal')
    licencia = models.ForeignKey(CAT_Licencia, on_delete=models.SET_NULL, null=True, blank=True, related_name='entrenadores')
    cedula_identidad = models.CharField(max_length=15, unique=True, db_index=True)
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Personal'
        verbose_name_plural = 'Personal'

    def __str__(self):
        cargo_nombre = self.cargo.nombre if self.cargo else 'Sin Cargo'
        return f"{self.nombres} {self.apellidos} ({cargo_nombre})"


class Categoria(models.Model):
    coordinador_supervisor = models.ForeignKey(
        Personal, on_delete=models.PROTECT, related_name='categorias_supervisadas'
    )
    delegado = models.ForeignKey(
        Personal, on_delete=models.PROTECT, related_name='categorias_delegadas',
        null=True, blank=True
    )
    genero = models.ForeignKey(CAT_Genero, on_delete=models.PROTECT, related_name='categorias')
    nombre = models.CharField(max_length=50, unique=True)
    anio_nacimiento_min = models.IntegerField()
    anio_nacimiento_max = models.IntegerField()

    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'

    def clean(self):
        super().clean()
        if self.anio_nacimiento_min and self.anio_nacimiento_max:
            if self.anio_nacimiento_min > self.anio_nacimiento_max:
                raise ValidationError({
                    'anio_nacimiento_min': 'El año mínimo de nacimiento no puede ser mayor al año máximo.'
                })

    def __str__(self):
        return self.nombre


class CategoriaEntrenadores(models.Model):
    categoria = models.ForeignKey(Categoria, on_delete=models.CASCADE, related_name='asignaciones_entrenadores')
    personal = models.ForeignKey(Personal, on_delete=models.CASCADE, related_name='categorias_asignadas')

    class Meta:
        verbose_name = 'Asignación de Entrenador a Categoría'
        verbose_name_plural = 'Asignaciones de Entrenadores a Categorías'
        unique_together = ('categoria', 'personal')

    def __str__(self):
        return f"{self.personal} en {self.categoria}"