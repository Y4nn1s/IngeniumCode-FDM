import hashlib
from datetime import date
from decimal import Decimal, ROUND_HALF_UP
from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils import timezone
from core.models import CatBanco, CatEstadoPago, CatMetodoPago

User = get_user_model()


# === Catálogos Base Locales (Se conservan por DATA PRESERVATION - no eliminar) ===

class CAT_Banco(models.Model):
    codigo_sudeban = models.CharField(max_length=4, unique=True)
    nombre = models.CharField(max_length=100, unique=True)
    activo = models.BooleanField(default=True)

    class Meta:
        verbose_name = 'Catálogo - Banco'
        verbose_name_plural = 'Catálogos - Bancos'

    def __str__(self):
        return f"{self.codigo_sudeban} - {self.nombre}"


class CAT_EstadoPago(models.Model):
    codigo = models.CharField(max_length=20, unique=True)
    descripcion = models.TextField(blank=True)

    class Meta:
        verbose_name = 'Catálogo - Estado de Pago'
        verbose_name_plural = 'Catálogos - Estados de Pago'

    def __str__(self):
        return self.codigo


class CAT_MetodoPago(models.Model):
    codigo = models.CharField(max_length=20, unique=True)
    nombre = models.CharField(max_length=50)

    class Meta:
        verbose_name = 'Catálogo - Método de Pago'
        verbose_name_plural = 'Catálogos - Métodos de Pago'

    def __str__(self):
        return self.nombre


# === Constantes de negocio ===
TOLERANCIA_COBERTURA_USD = Decimal('0.50')


# === Modelo TasaBCV ===
class TasaBCV(models.Model):
    """
    Registro histórico de la tasa BCV (Bolívares por USD).
    Campos según ERD V2.2: fecha (UK), tasa, fuente.
    """
    fecha = models.DateField(unique=True, db_index=True)
    tasa = models.DecimalField(
        max_digits=12, decimal_places=4,
        help_text="Bolívares por USD"
    )
    fuente = models.CharField(
        max_length=50, default='dolarapi',
        help_text="Origen: dolarapi, manual, etc."
    )
    capturada_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-fecha']
        verbose_name = 'Tasa BCV'
        verbose_name_plural = 'Tasas BCV'

    def __str__(self):
        return f"{self.fecha}: {self.tasa} Bs/USD ({self.fuente})"


# === Modelo Pago ===
class Pago(models.Model):
    representante = models.ForeignKey(
        'filiacion.Representante', on_delete=models.PROTECT, related_name='pagos'
    )
    concepto = models.CharField(
        max_length=200,
        help_text="Auto-generado desde mensualidades cubiertas, o texto libre"
    )

    # --- Campos legacy (catálogos locales, conservados para no perder datos) ---
    metodo_legacy = models.ForeignKey(
        CAT_MetodoPago, on_delete=models.PROTECT,
        related_name='pagos_legacy', null=True, blank=True,
    )
    banco_emisor_legacy = models.ForeignKey(
        CAT_Banco, on_delete=models.PROTECT,
        related_name='pagos_legacy', null=True, blank=True,
    )
    estado_legacy = models.ForeignKey(
        CAT_EstadoPago, on_delete=models.PROTECT,
        related_name='pagos_legacy', null=True, blank=True,
    )

    # --- Nuevas FK hacia catálogos centralizados de core (ERD V2.2) ---
    metodo = models.ForeignKey(
        CatMetodoPago, on_delete=models.PROTECT,
        related_name='pagos', null=True, blank=True,
    )
    banco_emisor = models.ForeignKey(
        CatBanco, on_delete=models.PROTECT,
        related_name='pagos', null=True, blank=True,
    )
    estado = models.ForeignKey(
        CatEstadoPago, on_delete=models.PROTECT,
        related_name='pagos', null=True, blank=True,
    )

    referencia = models.CharField(max_length=30, blank=True, db_index=True)

    # --- INMUTABILIDAD FINANCIERA (LEY VENEZOLANA / SENIAT) ---
    # Estos campos NO se normalizan: son snapshots históricos de auditoría.
    monto_bs = models.DecimalField(max_digits=14, decimal_places=2)
    tasa_bcv = models.DecimalField(
        max_digits=12, decimal_places=4, null=True, blank=True
    )
    monto_usd = models.DecimalField(
        max_digits=10, decimal_places=2, null=True, blank=True
    )

    fecha_pago = models.DateField()
    fecha_reporte = models.DateTimeField(auto_now_add=True)

    comprobante = models.FileField(upload_to='pagos/%Y/%m/')
    comprobante_hash = models.CharField(max_length=64, blank=True, db_index=True)

    motivo_rechazo = models.TextField(blank=True)

    revisado_por = models.ForeignKey(
        User, on_delete=models.PROTECT, null=True, blank=True,
        related_name='pagos_revisados'
    )
    revisado_en = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-fecha_reporte']
        verbose_name = 'Pago'
        verbose_name_plural = 'Pagos'

    def clean(self):
        super().clean()
        if self.monto_bs is not None and self.monto_bs <= Decimal('0.00'):
            raise ValidationError({'monto_bs': 'El monto en bolívares debe ser estrictamente mayor a cero.'})

        if self.fecha_pago and self.fecha_pago > date.today():
            raise ValidationError({'fecha_pago': 'La fecha del pago no puede ser posterior a la fecha actual.'})

    def save(self, *args, **kwargs):
        if self.comprobante and not self.comprobante_hash:
            self.comprobante_hash = self._calcular_hash()
        if self.monto_bs and self.tasa_bcv:
            self.monto_usd = (self.monto_bs / self.tasa_bcv).quantize(
                Decimal('0.01'), rounding=ROUND_HALF_UP
            )
        super().save(*args, **kwargs)

    def _calcular_hash(self):
        sha = hashlib.sha256()
        for chunk in self.comprobante.chunks():
            sha.update(chunk)
        self.comprobante.seek(0)
        return sha.hexdigest()

    def registrar_audit(self, accion, actor=None, estado_anterior='', estado_nuevo='', detalles=None):
        PagoAuditLog.objects.create(
            pago=self,
            accion=accion,
            actor=actor,
            estado_anterior=estado_anterior,
            estado_nuevo=estado_nuevo,
            detalles=detalles or {}
        )

    def __str__(self):
        estado_cod = self.estado.codigo if self.estado else 'SIN ESTADO'
        return f"Pago #{self.id} - {self.representante} - {estado_cod}"


# === Modelo Mensualidad ===
class Mensualidad(models.Model):
    """
    Representa el compromiso de pago mensual de un atleta.
    NOTA 3NF: No existe campo 'pagada: BOOLEAN' porque sería una dependencia
    transitiva — la solvencia se calcula a través del estado del pago asociado.
    Se expone como propiedad calculada 'esta_pagada'.
    """
    atleta = models.ForeignKey(
        'filiacion.Atleta', on_delete=models.CASCADE, related_name='mensualidades'
    )
    periodo_mes = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(12)],
        help_text="1-12"
    )
    periodo_anio = models.IntegerField(help_text="Ej: 2026")
    monto_usd = models.DecimalField(
        max_digits=8, decimal_places=2,
        help_text="Monto base en USD"
    )
    fecha_vencimiento = models.DateField()
    pago = models.ForeignKey(
        Pago, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='mensualidades_cubiertas',
        help_text="Pago que cubrió esta mensualidad"
    )
    creada_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [('atleta', 'periodo_mes', 'periodo_anio')]
        indexes = [
            models.Index(fields=['atleta']),
        ]
        ordering = ['-periodo_anio', '-periodo_mes']
        verbose_name = 'Mensualidad'
        verbose_name_plural = 'Mensualidades'

    @property
    def esta_pagada(self):
        """Calcula si está pagada vía el estado del pago asociado (3NF)."""
        return self.pago is not None and self.pago.estado and self.pago.estado.codigo == 'APROBADO'

    @property
    def pagada(self):
        """Alias de compatibilidad hacia esta_pagada."""
        return self.esta_pagada

    @property
    def vencida(self):
        return not self.esta_pagada and self.fecha_vencimiento < timezone.now().date()

    @property
    def etiqueta_periodo(self):
        meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
        return f"{meses[self.periodo_mes - 1]} {self.periodo_anio}"

    def __str__(self):
        return f"{self.atleta} - {self.periodo_mes}/{self.periodo_anio}"


# === Modelo PagoAuditLog (Event Sourcing) ===
class PagoAuditLog(models.Model):
    """
    Registro inmutable de eventos sobre pagos (Event Sourcing).
    NOTA ARQUITECTURAL: estado_anterior y estado_nuevo son CharField deliberadamente.
    Garantizan inmutabilidad histórica (snapshots) aunque el catálogo cambie.
    """
    pago = models.ForeignKey(Pago, on_delete=models.CASCADE, related_name='audit_log')
    actor = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='pagos_audit'
    )
    accion = models.CharField(max_length=50)
    estado_anterior = models.CharField(max_length=20, blank=True)
    estado_nuevo = models.CharField(max_length=20, blank=True)
    detalles = models.JSONField(default=dict, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [models.Index(fields=['pago', '-timestamp'])]
        verbose_name = 'Log de Auditoría de Pago'
        verbose_name_plural = 'Logs de Auditoría de Pagos'

    def __str__(self):
        return f"[{self.timestamp}] {self.accion} pago #{self.pago_id}"


# === Modelos de Patrocinio ===
class Patrocinante(models.Model):
    nombre_empresa = models.CharField(max_length=200)
    tipo_ente = models.CharField(max_length=20)
    persona_contacto = models.CharField(max_length=200)

    def __str__(self):
        return self.nombre_empresa


class Aporte(models.Model):
    patrocinante = models.ForeignKey(Patrocinante, on_delete=models.CASCADE, related_name='aportes')
    fecha_aporte = models.DateField()
    tipo = models.CharField(max_length=20)
    descripcion = models.TextField()
    valor_estimado_usd = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"Aporte de {self.patrocinante} ({self.fecha_aporte})"