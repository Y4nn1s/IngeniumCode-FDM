from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from core.models import CatTipoPartido, CatCondicionPartido, CatEstadoPartido


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

    # Catálogos centralizados de la app core
    tipo = models.ForeignKey(
        CatTipoPartido,
        on_delete=models.PROTECT,
        related_name='partidos',
        null=True,
        blank=True,
    )
    condicion = models.ForeignKey(
        CatCondicionPartido,
        on_delete=models.PROTECT,
        related_name='partidos',
        null=True,
        blank=True,
    )

    goles_favor_escuela = models.PositiveIntegerField(default=0)
    goles_contra_rival = models.PositiveIntegerField(default=0)

    # Workflow del partido (3NF): estado es FK a catálogo, no booleano procesado.
    estado = models.ForeignKey(
        CatEstadoPartido,
        on_delete=models.PROTECT,
        related_name='partidos',
        null=True,
        blank=True,
        help_text="Estado del partido (PROGRAMADO, EN_JUEGO, FINALIZADO, SUSPENDIDO, CANCELADO)"
    )

    class Meta:
        verbose_name = 'Partido'
        verbose_name_plural = 'Partidos'

    @property
    def procesado(self):
        """Compatibilidad: un partido está 'procesado' cuando está FINALIZADO."""
        return self.estado is not None and self.estado.codigo == 'FINALIZADO'

    @property
    def resultado(self):
        """Resultado calculado a partir de los goles. No es un campo de base de datos."""
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