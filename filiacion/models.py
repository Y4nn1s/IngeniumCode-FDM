from django.db import models

# --- Choices ---
LATERALIDAD_CHOICES = [
    ('DERECHO', 'Derecho'),
    ('IZQUIERDO', 'Izquierdo'),
    ('AMBIDIESTRO', 'Ambidiestro'),
]

POSICION_ATLETA_CHOICES = [
    ('POR', 'Portero'),
    ('DEF', 'Defensa'),
    ('MED', 'Mediocampista'),
    ('DEL', 'Delantero'),
]

# --- Modelos ---

class Representante(models.Model):
    cedula_identidad = models.CharField(max_length=15, unique=True)
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    telefono_principal = models.CharField(max_length=20)
    direccion_habitacion = models.TextField()
    correo_electronico = models.EmailField(unique=True)

    def __str__(self):
        return f"{self.nombres} {self.apellidos} (C.I: {self.cedula_identidad})"

class Atleta(models.Model):
    representante = models.ForeignKey(Representante, on_delete=models.CASCADE, related_name='atletas')
    categoria = models.ForeignKey('administracion.Categoria', on_delete=models.SET_NULL, null=True, related_name='atletas')
    cedula_escolar = models.CharField(max_length=20, unique=True, null=True, blank=True)
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    fecha_nacimiento = models.DateField()
    foto_perfil_url = models.URLField(max_length=255, blank=True, null=True)
    peso_kg = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    altura_mts = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    lateralidad = models.CharField(max_length=11, choices=LATERALIDAD_CHOICES)
    posicion = models.CharField(max_length=3, choices=POSICION_ATLETA_CHOICES)
    activo = models.BooleanField(default=True)
    becado = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.nombres} {self.apellidos}"