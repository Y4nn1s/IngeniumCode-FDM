from django.db import models

# --- Choices ---
ESTADO_PAGO_CHOICES = [
    ('PENDIENTE', 'Pendiente'),
    ('APROBADO', 'Aprobado'),
    ('RECHAZADO', 'Rechazado'),
]

METODO_PAGO_CHOICES = [
    ('EFECTIVO', 'Efectivo'),
    ('TRANSFERENCIA', 'Transferencia'),
    ('PAGO_MOVIL', 'Pago Móvil'),
    ('OTRO', 'Otro'),
]

TIPO_ENTE_PATROCINANTE_CHOICES = [
    ('PUBLICO', 'Público'),
    ('PRIVADO', 'Privado'),
    ('ONG', 'ONG'),
]

TIPO_APORTE_CHOICES = [
    ('MONETARIO', 'Monetario'),
    ('INSUMOS', 'Insumos'),
]

# --- Modelos ---

class Pago(models.Model):
    representante = models.ForeignKey('filiacion.Representante', on_delete=models.CASCADE, related_name='pagos')
    monto_bs = models.DecimalField(max_digits=14, decimal_places=2)
    tasa_bcv = models.DecimalField(max_digits=10, decimal_places=4)
    fecha_pago = models.DateTimeField()
    metodo = models.CharField(max_length=15, choices=METODO_PAGO_CHOICES)
    referencia = models.CharField(max_length=100, blank=True)
    estado = models.CharField(max_length=10, choices=ESTADO_PAGO_CHOICES, default='PENDIENTE')
    verificado_admin = models.BooleanField(default=False)

    def __str__(self):
        return f"Pago de {self.representante} - {self.fecha_pago.date()}"

class Patrocinante(models.Model):
    nombre_empresa = models.CharField(max_length=200)
    tipo_ente = models.CharField(max_length=10, choices=TIPO_ENTE_PATROCINANTE_CHOICES)
    persona_contacto = models.CharField(max_length=200)

    def __str__(self):
        return self.nombre_empresa

class Aporte(models.Model):
    patrocinante = models.ForeignKey(Patrocinante, on_delete=models.CASCADE, related_name='aportes')
    fecha_aporte = models.DateField()
    tipo = models.CharField(max_length=10, choices=TIPO_APORTE_CHOICES)
    descripcion = models.TextField()
    valor_estimado_usd = models.DecimalField(max_digits=12, decimal_places=2)

    def __str__(self):
        return f"Aporte de {self.patrocinante} ({self.fecha_aporte})"