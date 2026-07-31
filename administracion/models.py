from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from core.models import (
    CatCargo,
    CatLicencia,
    CatGenero,
)

User = get_user_model()


class Personal(models.Model):
    """Miembro del personal de la academia (entrenador, coordinador, delegado, etc.)."""
    usuario = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='perfil_personal'
    )
    cargo = models.ForeignKey(
        CatCargo,
        on_delete=models.PROTECT,
        related_name='personal'
    )
    licencia = models.ForeignKey(
        CatLicencia,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='personal'
    )
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
    """Categoría deportiva de la academia (ej. Sub-10, Sub-12) con su rango de edades y responsables."""
    coordinador_supervisor = models.ForeignKey(
        Personal,
        on_delete=models.PROTECT,
        related_name='categorias_coordinadas'
    )
    delegado = models.ForeignKey(
        Personal,
        on_delete=models.PROTECT,
        related_name='categorias_delegadas',
        null=True,
        blank=True,
    )
    genero = models.ForeignKey(
        CatGenero,
        on_delete=models.PROTECT,
        related_name='categorias'
    )
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
    """Tabla de asignación (M2M explícita) entre entrenadores y categorías."""
    categoria = models.ForeignKey(
        Categoria,
        on_delete=models.CASCADE,
        related_name='asignaciones_entrenadores'
    )
    personal = models.ForeignKey(
        Personal,
        on_delete=models.CASCADE,
        related_name='categorias_asignadas'
    )

    class Meta:
        verbose_name = 'Asignación de Entrenador a Categoría'
        verbose_name_plural = 'Asignaciones de Entrenadores a Categorías'
        unique_together = ('categoria', 'personal')

    def __str__(self):
        return f"{self.personal} en {self.categoria}"