from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


# === Catálogos Base (3NF) ===

class CAT_TipoPartido(models.Model):
    codigo = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=50)

    class Meta:
        verbose_name = 'Catálogo - Tipo de Partido'
        verbose_name_plural = 'Catálogos - Tipos de Partidos'

    def __str__(self):
        return self.nombre


class CAT_CondicionPartido(models.Model):
    codigo = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=50)

    class Meta:
        verbose_name = 'Catálogo - Condición de Partido'
        verbose_name_plural = 'Catálogos - Condiciones de Partidos'

    def __str__(self):
        return self.nombre


# === Modelos de Negocio ===

class Partido(models.Model):
    categoria = models.ForeignKey(
        'administracion.Categoria',
        on_delete=models.PROTECT,
        related_name='partidos',
        null=True,
        blank=True
    )
    fecha_hora = models.DateTimeField()
    equipo_rival = models.CharField(max_length=100)
    tipo = models.ForeignKey(CAT_TipoPartido, on_delete=models.PROTECT, related_name='partidos')
    condicion = models.ForeignKey(CAT_CondicionPartido, on_delete=models.PROTECT, related_name='partidos')
    goles_favor_escuela = models.PositiveIntegerField(default=0)
    goles_contra_rival = models.PositiveIntegerField(default=0)
    procesado = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Partido'
        verbose_name_plural = 'Partidos'

    @property
    def resultado(self):
        if self.goles_favor_escuela > self.goles_contra_rival:
            return 'VICTORIA'
        elif self.goles_favor_escuela < self.goles_contra_rival:
            return 'DERROTA'
        return 'EMPATE'

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
    calificacion_dt = models.DecimalField(
        max_digits=3, decimal_places=1,
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )

    class Meta:
        verbose_name = 'Estadística'
        verbose_name_plural = 'Estadísticas'
        unique_together = ('atleta', 'partido')

    def __str__(self):
        return f"Estadística de {self.atleta} en partido vs {self.partido.equipo_rival}"


class EvaluacionTecnica(models.Model):
    atleta = models.ForeignKey('filiacion.Atleta', on_delete=models.CASCADE, related_name='evaluaciones_tecnicas')
    entrenador = models.ForeignKey(
        'administracion.Personal', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='evaluaciones_tecnicas_realizadas'
    )
    fecha_evaluacion = models.DateField()
    control_balon = models.DecimalField(max_digits=3, decimal_places=1, validators=[MinValueValidator(1), MaxValueValidator(10)])
    conduccion = models.DecimalField(max_digits=3, decimal_places=1, validators=[MinValueValidator(1), MaxValueValidator(10)])
    pase_corto = models.DecimalField(max_digits=3, decimal_places=1, validators=[MinValueValidator(1), MaxValueValidator(10)])
    tiro = models.DecimalField(max_digits=3, decimal_places=1, validators=[MinValueValidator(1), MaxValueValidator(10)])
    inteligencia_tactica = models.DecimalField(max_digits=3, decimal_places=1, validators=[MinValueValidator(1), MaxValueValidator(10)])
    observaciones = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Evaluación Técnica'
        verbose_name_plural = 'Evaluaciones Técnicas'

    def __str__(self):
        return f"Evaluación Técnica de {self.atleta} ({self.fecha_evaluacion})"


class EvaluacionPsicosocial(models.Model):
    atleta = models.ForeignKey('filiacion.Atleta', on_delete=models.CASCADE, related_name='evaluaciones_psicosociales')
    evaluador = models.ForeignKey(
        'administracion.Personal', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='evaluaciones_psicosociales_realizadas'
    )
    fecha_evaluacion = models.DateField()
    compromiso = models.DecimalField(max_digits=3, decimal_places=1, validators=[MinValueValidator(1), MaxValueValidator(10)])
    puntualidad = models.DecimalField(max_digits=3, decimal_places=1, validators=[MinValueValidator(1), MaxValueValidator(10)])
    companerismo = models.DecimalField(max_digits=3, decimal_places=1, validators=[MinValueValidator(1), MaxValueValidator(10)])
    respeto = models.DecimalField(max_digits=3, decimal_places=1, validators=[MinValueValidator(1), MaxValueValidator(10)])
    manejo_frustracion = models.DecimalField(max_digits=3, decimal_places=1, validators=[MinValueValidator(1), MaxValueValidator(10)])
    observaciones_conductuales = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Evaluación Psicosocial'
        verbose_name_plural = 'Evaluaciones Psicosociales'

    def __str__(self):
        return f"Evaluación Psicosocial de {self.atleta} ({self.fecha_evaluacion})"