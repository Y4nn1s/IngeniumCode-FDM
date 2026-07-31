from datetime import date
from django.db import models
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError

User = get_user_model()


# === Catálogos Base (3NF) ===

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
        User, on_delete=models.CASCADE, null=True, blank=True,
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
    posicion = models.ForeignKey(
        CAT_Posicion, on_delete=models.PROTECT,
        null=True, blank=True, related_name='atletas'
    )
    lateralidad = models.ForeignKey(
        CAT_Lateralidad, on_delete=models.PROTECT,
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
    observacion_medica = models.TextField(blank=True)
    activo = models.BooleanField(default=True)
    becado = models.BooleanField(default=False)

    class Meta:
        verbose_name = 'Atleta'
        verbose_name_plural = 'Atletas'

    def clean(self):
        super().clean()
        hoy = date.today()

        if self.fecha_nacimiento:
            if self.fecha_nacimiento >= hoy:
                raise ValidationError({'fecha_nacimiento': 'La fecha de nacimiento no puede ser igual o posterior a la fecha actual.'})

            edad = hoy.year - self.fecha_nacimiento.year - (
                (hoy.month, hoy.day) < (self.fecha_nacimiento.month, self.fecha_nacimiento.day)
            )

            if edad >= 9 and not self.cedula_identidad:
                raise ValidationError({
                    'cedula_identidad': 'La cédula de identidad es obligatoria para atletas de 9 años o más (normativa SAIME).'
                })

            if not self.es_condicion_especial and self.peso_kg is not None:
                if self.peso_kg < 10.0 or self.peso_kg > 120.0:
                    raise ValidationError({'peso_kg': 'El peso debe estar entre 10.0 kg y 120.0 kg.'})
                if edad <= 6 and self.peso_kg > 35.0:
                    raise ValidationError({'peso_kg': 'El peso no puede superar 35.0 kg para atletas de 6 años o menos.'})

        if self.es_condicion_especial and not (self.observacion_medica and self.observacion_medica.strip()):
            raise ValidationError({
                'observacion_medica': 'Debe especificar las observaciones médicas para atletas con condición especial.'
            })

    def __str__(self):
        return f"{self.nombres} {self.apellidos}"