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


from core.models import (
    CatCargo as CoreCatCargo,
    CatLicencia as CoreCatLicencia,
    CatGenero as CoreCatGenero,
)


class Personal2(models.Model):
    """
    Versión refactorizada de Personal que referencia los catálogos centralizados
    de la app `core` en lugar de los catálogos locales de `administracion`.
    """
    id = models.AutoField(primary_key=True)
    usuario = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='perfil_personal2'
    )
    cargo = models.ForeignKey(
        CoreCatCargo,
        on_delete=models.PROTECT,
        related_name='personal2'
    )
    licencia = models.ForeignKey(
        CoreCatLicencia,
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        related_name='personal2'
    )
    cedula_identidad = models.CharField(max_length=15, unique=True, db_index=True)
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Personal (v2)'
        verbose_name_plural = 'Personal (v2)'

    def __str__(self):
        cargo_nombre = self.cargo.nombre if self.cargo else 'Sin Cargo'
        return f"{self.nombres} {self.apellidos} ({cargo_nombre})"


class Categoria2(models.Model):
    """
    Versión refactorizada de Categoria que referencia el catálogo CatGenero de `core`
    y los supervisores/delegados del nuevo modelo Personal2.
    """
    id = models.AutoField(primary_key=True)
    coordinador_supervisor = models.ForeignKey(
        Personal2,
        on_delete=models.PROTECT,
        related_name='categorias_coordinadas'
    )
    delegado = models.ForeignKey(
        Personal2,
        on_delete=models.PROTECT,
        related_name='categorias_delegadas2'
    )
    genero = models.ForeignKey(
        CoreCatGenero,
        on_delete=models.PROTECT,
        related_name='categorias2'
    )
    nombre = models.CharField(max_length=50, unique=True)
    anio_nacimiento_min = models.IntegerField()
    anio_nacimiento_max = models.IntegerField()

    class Meta:
        verbose_name = 'Categoría (v2)'
        verbose_name_plural = 'Categorías (v2)'

    def __str__(self):
        return self.nombre


class CategoriaEntrenadores2(models.Model):
    """
    Tabla puente M2M entre Categoria2 y Personal2.
    Versión refactorizada de CategoriaEntrenadores.
    """
    id = models.AutoField(primary_key=True)
    categoria = models.ForeignKey(
        Categoria2,
        on_delete=models.CASCADE,
        related_name='asignaciones_entrenadores2'
    )
    personal = models.ForeignKey(
        Personal2,
        on_delete=models.CASCADE,
        related_name='categorias_asignadas2'
    )

    class Meta:
        verbose_name = 'Asignación Entrenador a Categoría (v2)'
        verbose_name_plural = 'Asignaciones Entrenadores a Categorías (v2)'
        unique_together = ('categoria', 'personal')

    def __str__(self):
        return f"{self.personal} en {self.categoria}"