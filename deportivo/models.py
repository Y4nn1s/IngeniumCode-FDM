from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator

# --- Choices ---
TIPO_PARTIDO_CHOICES = [
    ('AMISTOSO', 'Amistoso'),
    ('OFICIAL', 'Oficial'),
]

CONDICION_PARTIDO_CHOICES = [
    ('CASA', 'Casa'),
    ('VISITANTE', 'Visitante'),
]

RESULTADO_PARTIDO_CHOICES = [
    ('VICTORIA', 'Victoria'),
    ('EMPATE', 'Empate'),
    ('DERROTA', 'Derrota'),
]

# --- Modelos ---

class Partido(models.Model):
    categoria = models.ForeignKey(
        'administracion.Categoria',
        on_delete=models.CASCADE,
        related_name='partidos',
        null=True,  # Temporal: remover después de asignar categorías a partidos existentes
        blank=True
    )
    fecha_hora = models.DateTimeField()
    equipo_rival = models.CharField(max_length=100)
    tipo = models.CharField(max_length=10, choices=TIPO_PARTIDO_CHOICES)
    condicion = models.CharField(max_length=10, choices=CONDICION_PARTIDO_CHOICES)
    goles_favor_escuela = models.PositiveIntegerField(default=0)
    goles_contra_rival = models.PositiveIntegerField(default=0)
    resultado = models.CharField(max_length=10, choices=RESULTADO_PARTIDO_CHOICES, blank=True)
    procesado = models.BooleanField(default=False)

    def __str__(self):
        return f"Partido vs {self.equipo_rival} el {self.fecha_hora.date()}"

class Estadistica(models.Model):
    atleta = models.ForeignKey('filiacion.Atleta', on_delete=models.CASCADE, related_name='estadisticas')
    partido = models.ForeignKey(Partido, on_delete=models.CASCADE, related_name='estadisticas')
    es_titular = models.BooleanField(default=False)
    minutos_jugados = models.PositiveIntegerField(default=0)
    goles = models.PositiveIntegerField(default=0)
    asistencias = models.PositiveIntegerField(default=0)
    tarjetas_amarillas = models.PositiveIntegerField(default=0)
    tarjetas_rojas = models.PositiveIntegerField(default=0)
    calificacion_dt = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(10)])

    class Meta:
        unique_together = ('atleta', 'partido')

    def __str__(self):
        return f"Estadística de {self.atleta} en partido vs {self.partido.equipo_rival}"

class Puntuacion(models.IntegerChoices):
    UNO = 1, '1'
    DOS = 2, '2'
    TRES = 3, '3'
    CUATRO = 4, '4'
    CINCO = 5, '5'
    SEIS = 6, '6'
    SIETE = 7, '7'
    OCHO = 8, '8'
    NUEVE = 9, '9'
    DIEZ = 10, '10'


class EvaluacionTecnica(models.Model):
    atleta = models.ForeignKey('filiacion.Atleta', on_delete=models.CASCADE, related_name='evaluaciones_tecnicas')
    entrenador = models.ForeignKey('administracion.Entrenador', on_delete=models.SET_NULL, null=True, related_name='evaluaciones_realizadas')
    fecha_evaluacion = models.DateField()
    velocidad = models.IntegerField(choices=Puntuacion.choices)
    resistencia = models.IntegerField(choices=Puntuacion.choices)
    control_balon = models.IntegerField(choices=Puntuacion.choices)
    pase_corto = models.IntegerField(choices=Puntuacion.choices)
    tiro = models.IntegerField(choices=Puntuacion.choices)
    inteligencia_tactica = models.IntegerField(choices=Puntuacion.choices)
    observaciones = models.TextField(blank=True)

    def __str__(self):
        return f"Evaluación Técnica de {self.atleta} ({self.fecha_evaluacion})"


class EvaluacionPsicosocial(models.Model):
    atleta = models.ForeignKey('filiacion.Atleta', on_delete=models.CASCADE, related_name='evaluaciones_psicosociales')
    coordinador_evaluador = models.ForeignKey('administracion.Coordinador', on_delete=models.SET_NULL, null=True, related_name='evaluaciones_psicosociales_realizadas')
    fecha_evaluacion = models.DateField()
    compromiso = models.IntegerField(choices=Puntuacion.choices)
    puntualidad = models.IntegerField(choices=Puntuacion.choices)
    companerismo = models.IntegerField(choices=Puntuacion.choices)
    respeto = models.IntegerField(choices=Puntuacion.choices)
    manejo_frustracion = models.IntegerField(choices=Puntuacion.choices)
    observaciones_conductuales = models.TextField(blank=True)

    def __str__(self):
        return f"Evaluación Psicosocial de {self.atleta} ({self.fecha_evaluacion})"