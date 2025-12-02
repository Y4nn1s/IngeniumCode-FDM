from django.db import models
from django.contrib.auth.models import User

# --- Choices ---
CARGO_COORDINADOR_CHOICES = [
    ('GENERAL', 'General'),
    ('DEPORTIVO', 'Deportivo'),
]

LICENCIA_ENTRENADOR_CHOICES = [
    ('FVF', 'Licencia FVF'),
    ('CONMEBOL', 'Licencia CONMEBOL'),
]

GENERO_CATEGORIA_CHOICES = [
    ('MASCULINO', 'Masculino'),
    ('FEMENINO', 'Femenino'),
    ('MIXTO', 'Mixto'),
]

# --- Modelos ---

class Coordinador(models.Model):
    usuario_sistema = models.OneToOneField(User, on_delete=models.CASCADE, related_name='coordinador_profile')
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    cargo = models.CharField(max_length=10, choices=CARGO_COORDINADOR_CHOICES)

    def __str__(self):
        return f"{self.nombres} {self.apellidos} ({self.get_cargo_display()})"

class Entrenador(models.Model):
    coordinador = models.ForeignKey(Coordinador, on_delete=models.SET_NULL, null=True, blank=True, related_name='entrenadores_a_cargo')
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    licencia = models.CharField(max_length=10, choices=LICENCIA_ENTRENADOR_CHOICES)
    telefono = models.CharField(max_length=20)
    activo = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.nombres} {self.apellidos}"

class Delegado(models.Model):
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    telefono = models.CharField(max_length=20)

    def __str__(self):
        return f"{self.nombres} {self.apellidos}"

class Categoria(models.Model):
    nombre = models.CharField(max_length=50, unique=True)
    anio_nacimiento_min = models.PositiveIntegerField()
    anio_nacimiento_max = models.PositiveIntegerField()
    genero = models.CharField(max_length=10, choices=GENERO_CATEGORIA_CHOICES)
    delegado = models.OneToOneField(Delegado, on_delete=models.SET_NULL, null=True, blank=True, related_name='categoria_delegada')
    coordinador_supervisor = models.ForeignKey(Coordinador, on_delete=models.SET_NULL, null=True, blank=True, related_name='categorias_supervisadas')
    entrenadores_asignados = models.ManyToManyField(Entrenador, blank=True, related_name='categorias_asignadas')

    def __str__(self):
        return self.nombre