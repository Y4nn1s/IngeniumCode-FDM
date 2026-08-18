from datetime import date
from decimal import Decimal
from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from core.models import CatPosicion, CatLateralidad
from core.validators import validar_cedula_venezolana

User = get_user_model()


# Curvas biológicas FDM (prevención de errores de tipeo; se omiten con
# es_condicion_especial=True). Los valores son máximos tolerados por edad.
MAX_PESO_KG_POR_EDAD = [
    (5, Decimal('35.00')),   # <= 5 años
    (7, Decimal('40.00')),   # Sub-7
    (9, Decimal('45.00')),   # Sub-9
    (11, Decimal('55.00')),  # Sub-11
    (13, Decimal('65.00')),  # Sub-13
    (15, Decimal('75.00')),  # Sub-15
    (99, Decimal('90.00')),  # > 15 años
]
PESO_MINIMO_KG = Decimal('10.00')

MAX_ALTURA_MTS_POR_EDAD = [
    (8, Decimal('1.60')),    # <= 8 años
    (10, Decimal('1.70')),   # Sub-10
    (12, Decimal('1.80')),   # Sub-12
    (14, Decimal('1.90')),   # Sub-14
    (99, Decimal('2.10')),   # > 14 años
]


def _limite_por_edad(edad, tabla):
    """Devuelve el límite de la banda que corresponde a la edad."""
    for tope, limite in tabla:
        if edad <= tope:
            return limite
    return tabla[-1][1]


class Representante(models.Model):
    usuario = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='representante',
        help_text="Cuenta de usuario asociada al representante"
    )
    cedula_identidad = models.CharField(
        max_length=15, unique=True, db_index=True,
        validators=[validar_cedula_venezolana]
    )
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    telefono_principal = models.CharField(max_length=20)
    correo_electronico = models.EmailField(unique=True)
    direccion_habitacion = models.TextField()
    telegram_chat_id = models.CharField(
        max_length=20, blank=True,
        help_text="ID de chat de Telegram para notificaciones"
    )

    class Meta:
        verbose_name = 'Representante'
        verbose_name_plural = 'Representantes'

    def __str__(self):
        return f"{self.nombres} {self.apellidos} (C.I: {self.cedula_identidad})"


class Atleta(models.Model):
    representante = models.ForeignKey(
        Representante, on_delete=models.CASCADE, related_name='atletas'
    )
    categoria = models.ForeignKey(
        'administracion.Categoria', on_delete=models.PROTECT,
        null=True, blank=True, related_name='atletas'
    )

    posicion = models.ForeignKey(
        CatPosicion, on_delete=models.PROTECT,
        null=True, blank=True, related_name='atletas'
    )
    lateralidad = models.ForeignKey(
        CatLateralidad, on_delete=models.PROTECT,
        null=True, blank=True, related_name='atletas'
    )
    numero_acta_nacimiento = models.CharField(
        max_length=50, blank=True,
        help_text="Partida/Acta de Nacimiento LOPNNA"
    )
    cedula_identidad = models.CharField(
        max_length=15, unique=True, null=True, blank=True, db_index=True,
        validators=[validar_cedula_venezolana],
        help_text="Obligatorio SAIME >= 9 años"
    )
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    fecha_nacimiento = models.DateField()
    foto_perfil = models.ImageField(upload_to='atletas/fotos/', blank=True, null=True)
    peso_kg = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    altura_mts = models.DecimalField(max_digits=4, decimal_places=2, null=True, blank=True)
    es_condicion_especial = models.BooleanField(default=False)
    observacion_medica = models.TextField(blank=True, null=True)
    activo = models.BooleanField(default=True)
    becado = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Atleta'
        verbose_name_plural = 'Atletas'

    def clean(self):
        """
        Validaciones de negocio: Ley SAIME (Venezuela) y controles biométricos.
        """
        super().clean()
        errores = {}

        # --- Cálculo de Edad ---
        hoy = date.today()
        edad = None
        if self.fecha_nacimiento:
            if self.fecha_nacimiento >= hoy:
                errores['fecha_nacimiento'] = 'La fecha de nacimiento no puede ser igual o posterior a la fecha actual.'
            else:
                edad = hoy.year - self.fecha_nacimiento.year - (
                    (hoy.month, hoy.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day)
                )

        # --- Ley SAIME (Venezuela) ---
        # Regla 1: El acta de nacimiento es obligatoria para todos los atletas.
        if not self.numero_acta_nacimiento or not self.numero_acta_nacimiento.strip():
            errores['numero_acta_nacimiento'] = 'El número de acta de nacimiento es obligatorio (LOPNNA).'

        # Regla 2: Cédula obligatoria a partir de los 9 años.
        if edad is not None and edad >= 9 and not self.cedula_identidad:
            errores['cedula_identidad'] = (
                'La cédula de identidad es obligatoria para atletas de 9 años o más (normativa SAIME).'
            )

        # --- Regla 3: Coherencia fecha de nacimiento ↔ categoría (FVF) ---
        if edad is not None and self.categoria_id is not None:
            anio_nacimiento = self.fecha_nacimiento.year
            try:
                anio_min = self.categoria.anio_nacimiento_min
                anio_max = self.categoria.anio_nacimiento_max
            except Exception:
                anio_min = anio_max = None
            if anio_min is not None and anio_max is not None:
                if not (anio_min <= anio_nacimiento <= anio_max):
                    errores['categoria'] = (
                        f"El año de nacimiento ({anio_nacimiento}) no coincide con la categoría "
                        f"{self.categoria.nombre} (años {anio_min}-{anio_max})."
                    )

        # --- Matriz Biométrica (Prevención de errores de tipeo) ---
        # Se omite por completo si el atleta tiene condición especial (datos
        # médicamente justificados en observacion_medica).
        if edad is not None and not self.es_condicion_especial:
            if self.peso_kg is not None:
                if self.peso_kg < PESO_MINIMO_KG:
                    errores['peso_kg'] = (
                        f"Peso anómalo para un atleta ({self.peso_kg} kg). Marque "
                        "'Condición Especial' si el dato es correcto."
                    )
                else:
                    peso_max = _limite_por_edad(edad, MAX_PESO_KG_POR_EDAD)
                    if self.peso_kg > peso_max:
                        errores['peso_kg'] = (
                            f"Peso anómalo para la edad ({self.peso_kg} kg, máx. {peso_max} kg). "
                            "Marque 'Condición Especial' si el dato es correcto."
                        )

            if self.altura_mts is not None:
                altura_max = _limite_por_edad(edad, MAX_ALTURA_MTS_POR_EDAD)
                if self.altura_mts > altura_max:
                    errores['altura_mts'] = (
                        f"Altura anómala para la edad ({self.altura_mts} mts, máx. {altura_max} mts). "
                        "Marque 'Condición Especial' si el dato es correcto."
                    )

        # Regla de condición especial: exige justificación médica.
        if self.es_condicion_especial:
            if not self.observacion_medica or not self.observacion_medica.strip():
                errores['observacion_medica'] = (
                    'Debe justificar médicamente la condición especial.'
                )

        if errores:
            raise ValidationError(errores)

    def __str__(self):
        return f"{self.nombres} {self.apellidos}"