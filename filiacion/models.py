from datetime import date
from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from core.models import CatPosicion, CatLateralidad

User = get_user_model()


# === Catálogos Base Locales (Se conservan por DATA PRESERVATION - no eliminar) ===

class CAT_Posicion(models.Model):
    codigo = models.CharField(max_length=10, unique=True)
    nombre = models.CharField(max_length=50)

    class Meta:
        verbose_name = 'Catálogo - Posición'
        verbose_name_plural = 'Catálogos - Posiciones'

    def __str__(self):
        return f"{self.nombre} ({self.codigo})"


class CAT_Lateralidad(models.Model):
    nombre = models.CharField(max_length=30, unique=True)

    class Meta:
        verbose_name = 'Catálogo - Lateralidad'
        verbose_name_plural = 'Catálogos - Lateralidades'

    def __str__(self):
        return self.nombre


# === Modelos de Negocio ===

class Representante(models.Model):
    usuario = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='representante',
        help_text="Cuenta de usuario asociada al representante"
    )
    cedula_identidad = models.CharField(max_length=15, unique=True, db_index=True)
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
    # FK hacia catálogos centralizados de core (ERD V2.2)
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
        Matriz de Validación - Fat Model (PRD Fase 3 / ERD V2.2).
        Centraliza las reglas de negocio: Ley SAIME + Biometría.
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

        # --- Matriz Biométrica (Prevención de errores de tipeo) ---
        if edad is not None and self.peso_kg is not None:
            if not self.es_condicion_especial:
                # Regla biométrica 1: Peso anómalo para menores de 5 años.
                if edad <= 5 and self.peso_kg > 35:
                    errores['peso_kg'] = (
                        "Peso anómalo para la edad. Marque 'Condición Especial' si el dato es correcto."
                    )
                # Regla biométrica 2: Peso anómalo para menores de 10 años.
                elif edad <= 10 and self.peso_kg > 60:
                    errores['peso_kg'] = (
                        "Peso anómalo para la edad. Marque 'Condición Especial' si el dato es correcto."
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