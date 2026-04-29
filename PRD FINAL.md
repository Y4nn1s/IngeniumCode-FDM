— Listo, va por el chat. Esta vez completo. Cópialo a un `.md` tú mismo cuando lo necesites.

---

# PRD — Módulo de Pagos Venezolanos + Eliminación de Logística

**Proyecto:** IngeniumCode-FDM — Escuela de Fútbol Comunitaria Infantil "Francisco de Miranda"
**Repositorio:** https://github.com/Y4nn1s/IngeniumCode-FDM
**Rama de trabajo:** `Módulo-de-Pagos`
**Versión:** 1.1 MVP (con Mensualidad, AuditLog, Rate Limiting)
**Fecha:** 2026-04-28
**Plazo de desarrollo:** 2 días apretados

---

## 0. Instrucciones para la IA ejecutora

Este documento es autocontenido. Tu tarea tiene **dos partes secuenciales**:

### Parte A — Limpieza (FASE 0)
Eliminar el módulo `logistica` completo. Es código legacy obsoleto. Detalle exacto en sección 4.

### Parte B — Desarrollo (FASES 1-8)
Implementar el módulo de pagos venezolanos descrito en las secciones 5 a 14.

### Reglas de ejecución

1. Lee el documento completo antes de codear.
2. Ejecuta las fases en orden estricto. No saltes pasos.
3. **Haz commit después de cada fase** con mensaje claro.
4. NO implementes nada marcado como "diferido" en sección 2.2.
5. Si una decisión técnica no está cubierta aquí, elige la opción más simple que funcione y documéntala como comentario.
6. Todo el código en español — nombres, comentarios, mensajes UI.
7. Si tienes dudas sobre archivos existentes, consulta la sección 3 antes de inventar.

---

## 1. Contexto del proyecto

IngeniumCode-FDM es una plataforma web Django para gestión integral de la Escuela de Fútbol Comunitaria Infantil "Francisco de Miranda". Maneja filiación de atletas, gestión deportiva, administración y finanzas.

La rama `Módulo-de-Pagos` está enfocada en construir el sistema de cobro de mensualidades. Hay código legacy del módulo `logistica` que se descartó y debe ser removido.

---

## 2. Alcance

### 2.1 Dentro del alcance

**Limpieza:**
- ✅ Eliminar app `logistica/` completa.
- ✅ Limpiar referencias en `INSTALLED_APPS` y URLs.
- ✅ Eliminar tablas `logistica_*` de la base de datos.

**Módulo de Pagos:**
- ✅ Modelo `Pago` ampliado con comprobante, banco, referencia, estado.
- ✅ **Modelo `Mensualidad`** con generación automática mensual.
- ✅ **Modelo `PagoAuditLog`** con histórico inmutable de cambios.
- ✅ Form web para reportar pago con selección de mensualidades a cubrir.
- ✅ Upload de comprobante (JPG/PNG/PDF, máx 5MB).
- ✅ Bandeja admin: listar, filtrar, ver, aprobar, rechazar.
- ✅ Bloqueo de comprobantes duplicados vía hash SHA-256.
- ✅ Bloqueo de referencias bancarias duplicadas activas (constraint DB).
- ✅ Tasa BCV ingresada manualmente por el admin al aprobar.
- ✅ Conversión Bs → USD calculada al aprobar.
- ✅ Notificación al representante vía Telegram bot.
- ✅ **Rate limiting** en endpoints sensibles.
- ✅ Management command para generar mensualidades del mes.

### 2.2 Fuera del alcance (V2)

- ❌ OCR automático de comprobantes.
- ❌ Riesgo score / auto-aprobación.
- ❌ Scraper automático de tasa BCV.
- ❌ Generación de recibo PDF.
- ❌ Validación MIME real con `python-magic`.
- ❌ Storage S3.
- ❌ Pagos parciales / planes de pago.
- ❌ Integración bancaria directa.
- ❌ Pasarelas de pago.
- ❌ Notificaciones por email/SMS/WhatsApp.

---

## 3. Estado actual del repositorio

### 3.1 Estructura

```
IngeniumCode-FDM/
├── administracion/
├── core/
├── deportivo/
├── filiacion/             ← Representante y Atleta
├── finanzas/              ← módulo a desarrollar
├── logistica/             ← ELIMINAR (Fase 0)
├── project_gestion/       ← settings.py y urls.py raíz
├── manage.py
├── requirements.txt
├── package.json
├── tailwind.config.js
└── .env
```

### 3.2 Stack técnico

- Python 3.x
- Django **5.2.9**
- PostgreSQL (`psycopg2-binary` 2.9.11)
- Pillow 12.0.0
- python-dotenv 1.2.1
- WeasyPrint 68.1 (no se usa en MVP)
- Tailwind CSS ^3.4.19

**Nuevas dependencias a agregar:**
```
requests>=2.31.0
django-ratelimit>=4.1.0
```

### 3.3 `project_gestion/settings.py` actual (modificar quirúrgicamente)

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    'core.apps.CoreConfig',
    'administracion.apps.AdministracionConfig',
    'filiacion.apps.FiliacionConfig',
    'deportivo.apps.DeportivoConfig',
    'finanzas.apps.FinanzasConfig',
    'logistica.apps.LogisticaConfig',  # ← ELIMINAR
]

LANGUAGE_CODE = 'es-ve'
TIME_ZONE = 'America/Caracas'
USE_I18N = True
USE_TZ = True

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'  # ← ya existe, NO duplicar
```

### 3.4 `project_gestion/urls.py` actual

```python
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('', include('filiacion.urls')),
    path('', include('deportivo.urls')),
    path('', include('administracion.urls')),
]

from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

`finanzas` NO está en URLs todavía — agregar en Fase 2.

### 3.5 Modelo `filiacion.Representante` existente

```python
class Representante(models.Model):
    cedula_identidad = models.CharField(max_length=15, unique=True)
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    telefono_principal = models.CharField(max_length=20)
    direccion_habitacion = models.TextField()
    correo_electronico = models.EmailField(unique=True)
```

**Agregar a `Representante`:**

```python
telegram_chat_id = models.CharField(max_length=20, blank=True,
    help_text="ID de chat de Telegram para notificaciones")
usuario = models.OneToOneField(
    'auth.User', on_delete=models.SET_NULL, null=True, blank=True,
    related_name='representante',
    help_text="Cuenta de usuario asociada al representante"
)
```

### 3.6 Modelo `filiacion.Atleta` existente

```python
class Atleta(models.Model):
    representante = models.ForeignKey(Representante, on_delete=models.CASCADE, related_name='atletas')
    categoria = models.ForeignKey('administracion.Categoria', ...)
    cedula_escolar = models.CharField(max_length=20, unique=True, null=True, blank=True)
    nombres = models.CharField(max_length=100)
    apellidos = models.CharField(max_length=100)
    fecha_nacimiento = models.DateField()
    activo = models.BooleanField(default=True)
    becado = models.BooleanField(default=False)
```

> **Verificar:** si existe campo de "monto de mensualidad" por atleta (puede estar en `Categoria`). Si existe, usarlo. Si no, asumir monto por defecto desde settings o `Categoria`.

### 3.7 Modelo `finanzas.Pago` actual (REEMPLAZAR)

```python
# DESCARTAR
class Pago(models.Model):
    representante = models.ForeignKey('filiacion.Representante', ...)
    monto_bs = models.DecimalField(max_digits=14, decimal_places=2)
    tasa_bcv = models.DecimalField(max_digits=10, decimal_places=4)
    fecha_pago = models.DateTimeField()
    metodo = models.CharField(max_length=15, choices=METODO_PAGO_CHOICES)
    referencia = models.CharField(max_length=100, blank=True)
    estado = models.CharField(max_length=10, choices=ESTADO_PAGO_CHOICES, default='PENDIENTE')
    verificado_admin = models.BooleanField(default=False)
```

`Patrocinante` y `Aporte` se preservan.

### 3.8 Módulo `logistica` (ELIMINAR)

Modelos `Proveedor` y `Compra`. `views.py` y `admin.py` vacíos. No tiene `urls.py`. No hay imports cruzados.

---

## 4. FASE 0 — Eliminación de Logística

**Tiempo:** 30 minutos.

### 4.1 Verificación previa

```bash
grep -r "from logistica" .
grep -r "import logistica" .
grep -r "'logistica\." .
grep -r "\"logistica\." .
```

Si aparece resultado fuera de `logistica/`, **DETENERSE y reportar**.

### 4.2 Pasos

**4.2.1** — Revertir migraciones:
```bash
python manage.py migrate logistica zero
```
Si nunca se aplicaron, ignorar error y continuar.

**4.2.2** — Quitar de `INSTALLED_APPS` en `project_gestion/settings.py`:
```python
'logistica.apps.LogisticaConfig',  # ← BORRAR esta línea
```

**4.2.3** — Eliminar directorio:
```bash
rm -rf logistica/
```

**4.2.4** — Verificar:
```bash
python manage.py check
python manage.py runserver
```

**4.2.5** — Commit:
```bash
git add -A
git commit -m "chore: eliminar módulo logística obsoleto"
```

---

## 5. FASE 1 — Modelos

**Tiempo:** 3 horas.

### 5.1 Modificar `filiacion/models.py`

Agregar al modelo `Representante` los dos campos nuevos (`telegram_chat_id` y `usuario`). NO modificar campos existentes.

### 5.2 Reemplazar `finanzas/models.py` completo

```python
# finanzas/models.py
import hashlib
from decimal import Decimal
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()

# === Choices ===
ESTADO_PAGO_CHOICES = [
    ('PENDIENTE', 'Pendiente'),
    ('APROBADO',  'Aprobado'),
    ('RECHAZADO', 'Rechazado'),
]

METODO_PAGO_CHOICES = [
    ('PAGO_MOVIL',     'Pago Móvil'),
    ('TRANSFERENCIA',  'Transferencia'),
    ('EFECTIVO_BS',    'Efectivo Bs'),
    ('EFECTIVO_USD',   'Efectivo USD'),
    ('OTRO',           'Otro'),
]

BANCO_CHOICES = [
    ('0102', 'Banco de Venezuela'),
    ('0105', 'Mercantil'),
    ('0108', 'BBVA Provincial'),
    ('0114', 'Bancaribe'),
    ('0134', 'Banesco'),
    ('0151', 'BFC Banco Fondo Común'),
    ('0156', '100% Banco'),
    ('0163', 'Banco del Tesoro'),
    ('0172', 'Bancamiga'),
    ('0174', 'Banplus'),
    ('0175', 'Bicentenario'),
    ('0191', 'BNC Nacional de Crédito'),
    ('OTRO', 'Otro'),
]

ACCION_AUDIT_CHOICES = [
    ('CREADO',          'Creado'),
    ('APROBADO',        'Aprobado'),
    ('RECHAZADO',       'Rechazado'),
    ('EDITADO',         'Editado'),
    ('ANULADO',         'Anulado'),
    ('MENSUALIDADES_VINCULADAS', 'Mensualidades vinculadas'),
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


# === Modelo Mensualidad ===
class Mensualidad(models.Model):
    """Cada mensualidad que un atleta debe pagar. Una fila por mes por atleta."""
    atleta = models.ForeignKey(
        'filiacion.Atleta', on_delete=models.CASCADE, related_name='mensualidades'
    )
    periodo_mes = models.IntegerField(help_text="1-12")
    periodo_anio = models.IntegerField(help_text="Ej: 2026")
    monto_usd = models.DecimalField(
        max_digits=8, decimal_places=2,
        help_text="Monto base en USD"
    )
    fecha_vencimiento = models.DateField()
    pagada = models.BooleanField(default=False, db_index=True)
    pago = models.ForeignKey(
        'Pago', on_delete=models.SET_NULL, null=True, blank=True,
        related_name='mensualidades_cubiertas',
        help_text="Pago que cubrió esta mensualidad"
    )
    creada_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [('atleta', 'periodo_mes', 'periodo_anio')]
        indexes = [
            models.Index(fields=['pagada', 'fecha_vencimiento']),
            models.Index(fields=['atleta', 'pagada']),
        ]
        ordering = ['-periodo_anio', '-periodo_mes']

    def __str__(self):
        return f"{self.atleta} - {self.periodo_mes}/{self.periodo_anio}"

    @property
    def vencida(self):
        return not self.pagada and self.fecha_vencimiento < timezone.now().date()

    @property
    def etiqueta_periodo(self):
        meses = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
        return f"{meses[self.periodo_mes - 1]} {self.periodo_anio}"


# === Modelo Pago ===
class Pago(models.Model):
    representante = models.ForeignKey(
        'filiacion.Representante', on_delete=models.PROTECT, related_name='pagos'
    )
    concepto = models.CharField(
        max_length=200,
        help_text="Auto-generado desde mensualidades cubiertas, o texto libre"
    )

    metodo = models.CharField(max_length=15, choices=METODO_PAGO_CHOICES)
    banco_emisor = models.CharField(max_length=4, choices=BANCO_CHOICES, blank=True)
    referencia = models.CharField(max_length=30, blank=True, db_index=True)

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

    estado = models.CharField(
        max_length=10, choices=ESTADO_PAGO_CHOICES, default='PENDIENTE'
    )
    motivo_rechazo = models.TextField(blank=True)

    revisado_por = models.ForeignKey(
        User, on_delete=models.PROTECT, null=True, blank=True,
        related_name='pagos_revisados'
    )
    revisado_en = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-fecha_reporte']
        constraints = [
            models.UniqueConstraint(
                fields=['banco_emisor', 'referencia'],
                condition=models.Q(estado__in=['PENDIENTE', 'APROBADO']),
                name='uniq_referencia_activa'
            ),
        ]

    def save(self, *args, **kwargs):
        if self.comprobante and not self.comprobante_hash:
            self.comprobante_hash = self._calcular_hash()
        if self.monto_bs and self.tasa_bcv:
            self.monto_usd = self.monto_bs / self.tasa_bcv
        super().save(*args, **kwargs)

    def _calcular_hash(self):
        sha = hashlib.sha256()
        for chunk in self.comprobante.chunks():
            sha.update(chunk)
        self.comprobante.seek(0)
        return sha.hexdigest()

    def registrar_audit(self, accion, actor=None, estado_anterior='', estado_nuevo='', detalles=None):
        """Helper para registrar entradas en el audit log."""
        PagoAuditLog.objects.create(
            pago=self,
            accion=accion,
            actor=actor,
            estado_anterior=estado_anterior,
            estado_nuevo=estado_nuevo,
            detalles=detalles or {}
        )

    def __str__(self):
        return f"Pago #{self.id} - {self.representante} - {self.estado}"


# === Modelo PagoAuditLog ===
class PagoAuditLog(models.Model):
    """Registro inmutable de cada cambio sobre un pago. Append-only."""
    pago = models.ForeignKey(Pago, on_delete=models.CASCADE, related_name='audit_log')
    accion = models.CharField(max_length=30, choices=ACCION_AUDIT_CHOICES)
    estado_anterior = models.CharField(max_length=15, blank=True)
    estado_nuevo = models.CharField(max_length=15, blank=True)
    actor = models.ForeignKey(
        User, on_delete=models.PROTECT, null=True, blank=True,
        related_name='pagos_audit'
    )
    detalles = models.JSONField(default=dict, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True, db_index=True)

    class Meta:
        ordering = ['-timestamp']
        indexes = [models.Index(fields=['pago', '-timestamp'])]

    def __str__(self):
        return f"[{self.timestamp}] {self.accion} pago #{self.pago_id}"


# === Modelos preexistentes (preservar) ===
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
```

### 5.3 Migración

```bash
python manage.py makemigrations filiacion finanzas
python manage.py migrate
```

Si la migración del `Pago` viejo falla por incompatibilidad y no hay datos productivos: eliminar todas las migraciones de `finanzas/migrations/` excepto `__init__.py` y regenerar.

### 5.4 Crear `finanzas/admin.py`

```python
# finanzas/admin.py
from django.contrib import admin
from .models import Pago, PagoAuditLog, Mensualidad, Patrocinante, Aporte


class PagoAuditLogInline(admin.TabularInline):
    model = PagoAuditLog
    extra = 0
    readonly_fields = ('timestamp', 'accion', 'estado_anterior', 'estado_nuevo', 'actor', 'detalles')
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Pago)
class PagoAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'representante', 'concepto', 'metodo',
        'monto_bs', 'monto_usd', 'estado', 'fecha_reporte'
    )
    list_filter = ('estado', 'metodo', 'banco_emisor', 'fecha_pago')
    search_fields = (
        'representante__cedula_identidad',
        'representante__nombres',
        'representante__apellidos',
        'referencia',
        'concepto'
    )
    readonly_fields = (
        'comprobante_hash', 'fecha_reporte',
        'revisado_por', 'revisado_en', 'monto_usd'
    )
    ordering = ('-fecha_reporte',)
    date_hierarchy = 'fecha_pago'
    inlines = [PagoAuditLogInline]


@admin.register(Mensualidad)
class MensualidadAdmin(admin.ModelAdmin):
    list_display = ('atleta', 'periodo_mes', 'periodo_anio', 'monto_usd', 'fecha_vencimiento', 'pagada')
    list_filter = ('pagada', 'periodo_anio', 'periodo_mes')
    search_fields = ('atleta__nombres', 'atleta__apellidos', 'atleta__cedula_escolar')
    date_hierarchy = 'fecha_vencimiento'


@admin.register(PagoAuditLog)
class PagoAuditLogAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'pago', 'accion', 'actor')
    list_filter = ('accion', 'timestamp')
    search_fields = ('pago__id', 'actor__username')
    readonly_fields = ('pago', 'accion', 'estado_anterior', 'estado_nuevo', 'actor', 'detalles', 'timestamp')

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Patrocinante)
class PatrocinanteAdmin(admin.ModelAdmin):
    list_display = ('nombre_empresa', 'tipo_ente', 'persona_contacto')
    search_fields = ('nombre_empresa',)


@admin.register(Aporte)
class AporteAdmin(admin.ModelAdmin):
    list_display = ('patrocinante', 'fecha_aporte', 'tipo', 'valor_estimado_usd')
    list_filter = ('tipo', 'fecha_aporte')
```

### 5.5 Commit

```bash
git add -A
git commit -m "feat(finanzas): modelos Pago, Mensualidad y PagoAuditLog"
```

---

## 6. FASE 2 — Forms y URLs

**Tiempo:** 45 minutos.

### 6.1 Crear `finanzas/forms.py`

```python
# finanzas/forms.py
from django import forms
from django.utils import timezone
from .models import Pago, Mensualidad


class ReportarPagoForm(forms.ModelForm):
    mensualidades = forms.ModelMultipleChoiceField(
        queryset=Mensualidad.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        help_text="Selecciona qué mensualidades cubre este pago"
    )

    class Meta:
        model = Pago
        fields = [
            'metodo', 'banco_emisor', 'referencia',
            'monto_bs', 'fecha_pago', 'comprobante'
        ]
        widgets = {
            'fecha_pago': forms.DateInput(attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        representante = kwargs.pop('representante', None)
        super().__init__(*args, **kwargs)
        if representante:
            atletas = representante.atletas.filter(activo=True)
            self.fields['mensualidades'].queryset = Mensualidad.objects.filter(
                atleta__in=atletas, pagada=False
            ).select_related('atleta').order_by('fecha_vencimiento')

    def clean_comprobante(self):
        f = self.cleaned_data['comprobante']
        if f.size > 5 * 1024 * 1024:
            raise forms.ValidationError('El comprobante no puede superar 5MB.')
        ext = f.name.lower().rsplit('.', 1)[-1]
        if ext not in ('jpg', 'jpeg', 'png', 'pdf'):
            raise forms.ValidationError('Solo se aceptan archivos JPG, PNG o PDF.')
        return f

    def clean_fecha_pago(self):
        fecha = self.cleaned_data['fecha_pago']
        if fecha > timezone.now().date():
            raise forms.ValidationError('La fecha de pago no puede ser futura.')
        return fecha

    def clean(self):
        cleaned = super().clean()
        ref = cleaned.get('referencia')
        banco = cleaned.get('banco_emisor')
        if ref and banco:
            existe = Pago.objects.filter(
                banco_emisor=banco,
                referencia=ref,
                estado__in=['PENDIENTE', 'APROBADO']
            ).exists()
            if existe:
                raise forms.ValidationError(
                    f'Ya existe un pago activo con referencia {ref} de ese banco.'
                )
        return cleaned


class AprobarPagoForm(forms.Form):
    tasa_bcv = forms.DecimalField(
        max_digits=12, decimal_places=4, min_value=0,
        help_text='Tasa BCV del día del pago (Bs por USD)'
    )


class RechazarPagoForm(forms.Form):
    motivo = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        max_length=500,
        help_text='Explica al representante por qué se rechaza.'
    )
```

### 6.2 Crear `finanzas/urls.py`

```python
# finanzas/urls.py
from django.urls import path
from . import views

app_name = 'finanzas'

urlpatterns = [
    path('reportar/', views.reportar_pago, name='reportar'),
    path('mis-pagos/', views.mis_pagos, name='mis_pagos'),

    path('admin/bandeja/', views.bandeja_admin, name='bandeja'),
    path('admin/<int:pk>/', views.detalle_admin, name='detalle'),
    path('admin/<int:pk>/aprobar/', views.aprobar, name='aprobar'),
    path('admin/<int:pk>/rechazar/', views.rechazar, name='rechazar'),

    path('telegram/webhook/', views.telegram_webhook, name='telegram_webhook'),
]
```

### 6.3 Modificar `project_gestion/urls.py`

Agregar UNA línea:

```python
urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('', include('filiacion.urls')),
    path('', include('deportivo.urls')),
    path('', include('administracion.urls')),
    path('finanzas/', include('finanzas.urls', namespace='finanzas')),  # ← NUEVO
]
```

### 6.4 Configurar cache para rate limiting en `settings.py`

Agregar al final de `settings.py`:

```python
# Cache para rate limiting (usa la BD, sin Redis)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.db.DatabaseCache',
        'LOCATION': 'django_cache_table',
    }
}

# Rate limiting
RATELIMIT_ENABLE = True
```

Crear la tabla de cache:

```bash
python manage.py createcachetable
```

### 6.5 Commit

```bash
git add -A
git commit -m "feat(finanzas): forms con selección de mensualidades + cache para rate limit"
```

---

## 7. FASE 3 — Vistas con Rate Limiting y AuditLog

**Tiempo:** 2 horas.

### 7.1 Crear `finanzas/telegram_bot.py`

```python
# finanzas/telegram_bot.py
import os
import logging
import requests

logger = logging.getLogger(__name__)
BOT_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN', '')
API_URL = f'https://api.telegram.org/bot{BOT_TOKEN}' if BOT_TOKEN else None


def enviar_mensaje(chat_id, texto):
    if not BOT_TOKEN or not chat_id:
        logger.warning('Telegram: token o chat_id ausente.')
        return False
    try:
        r = requests.post(
            f'{API_URL}/sendMessage',
            json={'chat_id': chat_id, 'text': texto, 'parse_mode': 'HTML'},
            timeout=5
        )
        if not r.ok:
            logger.error(f'Telegram error: {r.status_code} {r.text}')
        return r.ok
    except Exception as e:
        logger.exception(f'Telegram exception: {e}')
        return False


def notificar_representante(representante, texto):
    if representante.telegram_chat_id:
        return enviar_mensaje(representante.telegram_chat_id, texto)
    return False
```

### 7.2 Reemplazar `finanzas/views.py`

```python
# finanzas/views.py
import hashlib
import json
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.utils import timezone
from django.db import IntegrityError, transaction
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django_ratelimit.decorators import ratelimit

from .models import Pago, Mensualidad, PagoAuditLog
from .forms import ReportarPagoForm, AprobarPagoForm, RechazarPagoForm
from .telegram_bot import notificar_representante, enviar_mensaje


def es_admin(u):
    return u.is_authenticated and (
        u.is_staff or u.groups.filter(name='Tesoreria').exists()
    )


# === Vistas del representante ===

@login_required
@ratelimit(key='user', rate='5/h', method='POST', block=True)
def reportar_pago(request):
    if not hasattr(request.user, 'representante') or request.user.representante is None:
        messages.error(request, 'Tu usuario no está asociado a un representante.')
        return redirect('/')

    rep = request.user.representante

    if request.method == 'POST':
        form = ReportarPagoForm(request.POST, request.FILES, representante=rep)
        if form.is_valid():
            with transaction.atomic():
                pago = form.save(commit=False)
                pago.representante = rep

                # Hash anti-duplicado
                sha = hashlib.sha256()
                for chunk in pago.comprobante.chunks():
                    sha.update(chunk)
                pago.comprobante.seek(0)
                comp_hash = sha.hexdigest()

                if Pago.objects.filter(comprobante_hash=comp_hash).exists():
                    messages.error(request, 'Este comprobante ya fue reportado anteriormente.')
                    return render(request, 'finanzas/reportar.html', {'form': form})

                pago.comprobante_hash = comp_hash

                # Construir concepto desde mensualidades seleccionadas
                mensualidades = form.cleaned_data.get('mensualidades')
                if mensualidades:
                    etiquetas = [f"{m.atleta.nombres} {m.etiqueta_periodo}" for m in mensualidades]
                    pago.concepto = " + ".join(etiquetas)[:200]
                else:
                    pago.concepto = "Pago sin mensualidad asociada"

                try:
                    pago.save()
                except IntegrityError:
                    messages.error(
                        request,
                        'Esta referencia bancaria ya está registrada en otro pago activo.'
                    )
                    return render(request, 'finanzas/reportar.html', {'form': form})

                # AuditLog: creación
                pago.registrar_audit(
                    accion='CREADO',
                    actor=request.user,
                    estado_nuevo='PENDIENTE',
                    detalles={
                        'monto_bs': str(pago.monto_bs),
                        'metodo': pago.metodo,
                        'mensualidades_ids': [m.id for m in mensualidades] if mensualidades else [],
                    }
                )

                # Vincular mensualidades (sin marcarlas pagadas hasta aprobación)
                if mensualidades:
                    for m in mensualidades:
                        m.pago = pago
                        m.save()

            messages.success(
                request,
                f'Pago #{pago.id} recibido. Te notificaremos al verificarlo.'
            )
            return redirect('finanzas:mis_pagos')
    else:
        form = ReportarPagoForm(representante=rep)

    return render(request, 'finanzas/reportar.html', {'form': form})


@login_required
def mis_pagos(request):
    if not hasattr(request.user, 'representante') or request.user.representante is None:
        messages.error(request, 'Tu usuario no está asociado a un representante.')
        return redirect('/')

    rep = request.user.representante
    pagos = Pago.objects.filter(representante=rep)
    mensualidades_pendientes = Mensualidad.objects.filter(
        atleta__representante=rep, pagada=False
    ).select_related('atleta')

    return render(request, 'finanzas/mis_pagos.html', {
        'pagos': pagos,
        'mensualidades_pendientes': mensualidades_pendientes,
    })


# === Vistas del administrador ===

@user_passes_test(es_admin)
def bandeja_admin(request):
    estado = request.GET.get('estado', 'PENDIENTE')
    if estado not in ['PENDIENTE', 'APROBADO', 'RECHAZADO', 'TODOS']:
        estado = 'PENDIENTE'

    if estado == 'TODOS':
        pagos = Pago.objects.all().select_related('representante')
    else:
        pagos = Pago.objects.filter(estado=estado).select_related('representante')

    return render(request, 'finanzas/bandeja.html', {
        'pagos': pagos,
        'estado_actual': estado,
    })


@user_passes_test(es_admin)
def detalle_admin(request, pk):
    pago = get_object_or_404(Pago, pk=pk)
    audit = pago.audit_log.all()[:20]
    return render(request, 'finanzas/detalle.html', {
        'pago': pago,
        'audit_log': audit,
        'aprobar_form': AprobarPagoForm(),
        'rechazar_form': RechazarPagoForm(),
    })


@user_passes_test(es_admin)
@ratelimit(key='user', rate='30/m', method='POST', block=True)
def aprobar(request, pk):
    pago = get_object_or_404(Pago, pk=pk)
    if pago.estado != 'PENDIENTE':
        messages.warning(request, 'Solo se pueden aprobar pagos pendientes.')
        return redirect('finanzas:detalle', pk=pk)

    if request.method == 'POST':
        form = AprobarPagoForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                estado_anterior = pago.estado
                pago.tasa_bcv = form.cleaned_data['tasa_bcv']
                pago.estado = 'APROBADO'
                pago.revisado_por = request.user
                pago.revisado_en = timezone.now()
                pago.save()

                # Marcar mensualidades vinculadas como pagadas
                mensualidades = pago.mensualidades_cubiertas.all()
                for m in mensualidades:
                    m.pagada = True
                    m.save()

                # AuditLog
                pago.registrar_audit(
                    accion='APROBADO',
                    actor=request.user,
                    estado_anterior=estado_anterior,
                    estado_nuevo='APROBADO',
                    detalles={
                        'tasa_bcv': str(pago.tasa_bcv),
                        'monto_usd': str(pago.monto_usd),
                        'mensualidades_pagadas': [m.id for m in mensualidades],
                    }
                )

                if mensualidades.exists():
                    pago.registrar_audit(
                        accion='MENSUALIDADES_VINCULADAS',
                        actor=request.user,
                        detalles={'count': mensualidades.count()}
                    )

            notificar_representante(
                pago.representante,
                f'✅ Tu pago #{pago.id} de {pago.monto_bs} Bs '
                f'({pago.monto_usd} USD) fue APROBADO.\n'
                f'Concepto: {pago.concepto}'
            )
            messages.success(request, f'Pago #{pago.id} aprobado.')
        else:
            messages.error(request, 'Tasa BCV inválida.')

    return redirect('finanzas:bandeja')


@user_passes_test(es_admin)
@ratelimit(key='user', rate='30/m', method='POST', block=True)
def rechazar(request, pk):
    pago = get_object_or_404(Pago, pk=pk)
    if pago.estado != 'PENDIENTE':
        messages.warning(request, 'Solo se pueden rechazar pagos pendientes.')
        return redirect('finanzas:detalle', pk=pk)

    if request.method == 'POST':
        form = RechazarPagoForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                estado_anterior = pago.estado
                pago.estado = 'RECHAZADO'
                pago.motivo_rechazo = form.cleaned_data['motivo']
                pago.revisado_por = request.user
                pago.revisado_en = timezone.now()
                pago.save()

                # Desvincular mensualidades (siguen disponibles para otro pago)
                pago.mensualidades_cubiertas.update(pago=None)

                pago.registrar_audit(
                    accion='RECHAZADO',
                    actor=request.user,
                    estado_anterior=estado_anterior,
                    estado_nuevo='RECHAZADO',
                    detalles={'motivo': pago.motivo_rechazo}
                )

            notificar_representante(
                pago.representante,
                f'❌ Tu pago #{pago.id} fue RECHAZADO.\n'
                f'Motivo: {pago.motivo_rechazo}'
            )
            messages.success(request, f'Pago #{pago.id} rechazado.')
        else:
            messages.error(request, 'Motivo de rechazo requerido.')

    return redirect('finanzas:bandeja')


# === Webhook Telegram ===

@csrf_exempt
@ratelimit(key='ip', rate='60/m', block=True)
def telegram_webhook(request):
    if request.method != 'POST':
        return JsonResponse({'ok': False})

    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'ok': False})

    msg = data.get('message', {})
    text = msg.get('text', '')
    chat_id = msg.get('chat', {}).get('id')

    if not chat_id:
        return JsonResponse({'ok': True})

    if text.startswith('/start '):
        from filiacion.models import Representante
        token = text.split(' ', 1)[1].strip()
        try:
            rep = Representante.objects.get(cedula_identidad=token)
            rep.telegram_chat_id = str(chat_id)
            rep.save()
            enviar_mensaje(
                chat_id,
                f'✅ Listo, {rep.nombres}. Recibirás notificaciones aquí.'
            )
        except Representante.DoesNotExist:
            enviar_mensaje(
                chat_id,
                '❌ Cédula no encontrada. Envía: /start TU_CEDULA'
            )
    elif text == '/start':
        enviar_mensaje(
            chat_id,
            'Hola. Para asociar tu cuenta envía: /start TU_CEDULA'
        )

    return JsonResponse({'ok': True})
```

### 7.3 Commit

```bash
git add -A
git commit -m "feat(finanzas): vistas con rate limiting, audit log y vinculación de mensualidades"
```

---

## 8. FASE 4 — Management Command para Mensualidades

**Tiempo:** 1 hora.

### 8.1 Crear estructura

```bash
mkdir -p finanzas/management/commands
touch finanzas/management/__init__.py
touch finanzas/management/commands/__init__.py
```

### 8.2 Crear `finanzas/management/commands/generar_mensualidades.py`

```python
# finanzas/management/commands/generar_mensualidades.py
import calendar
from datetime import date
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils import timezone
from filiacion.models import Atleta
from finanzas.models import Mensualidad


# Monto por defecto si el atleta/categoría no define uno propio
MONTO_DEFAULT_USD = Decimal('15.00')


class Command(BaseCommand):
    help = 'Genera mensualidades para todos los atletas activos del mes especificado.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--mes', type=int, default=None,
            help='Mes (1-12). Default: mes actual.'
        )
        parser.add_argument(
            '--anio', type=int, default=None,
            help='Año. Default: año actual.'
        )
        parser.add_argument(
            '--monto', type=str, default=None,
            help=f'Monto USD. Default: {MONTO_DEFAULT_USD} o el de la categoría.'
        )
        parser.add_argument(
            '--dia-vencimiento', type=int, default=10,
            help='Día del mes en que vence. Default: 10.'
        )

    def handle(self, *args, **opts):
        hoy = timezone.now().date()
        mes = opts['mes'] or hoy.month
        anio = opts['anio'] or hoy.year
        dia_venc = opts['dia_vencimiento']
        monto_override = Decimal(opts['monto']) if opts['monto'] else None

        # Validar día de vencimiento contra el mes
        ultimo_dia = calendar.monthrange(anio, mes)[1]
        dia_venc = min(dia_venc, ultimo_dia)
        fecha_venc = date(anio, mes, dia_venc)

        atletas = Atleta.objects.filter(activo=True).exclude(becado=True)

        creadas = 0
        existentes = 0

        for atleta in atletas:
            # Determinar monto: parámetro CLI > monto de categoría (si existe) > default
            if monto_override is not None:
                monto = monto_override
            else:
                # Si Categoria tiene campo de monto, usarlo. Si no, default.
                monto = getattr(atleta.categoria, 'monto_mensualidad_usd', None) or MONTO_DEFAULT_USD

            mensualidad, created = Mensualidad.objects.get_or_create(
                atleta=atleta,
                periodo_mes=mes,
                periodo_anio=anio,
                defaults={
                    'monto_usd': monto,
                    'fecha_vencimiento': fecha_venc,
                }
            )
            if created:
                creadas += 1
            else:
                existentes += 1

        self.stdout.write(self.style.SUCCESS(
            f'Mensualidades {mes}/{anio}: {creadas} creadas, {existentes} ya existían.'
        ))
```

### 8.3 Probar

```bash
python manage.py generar_mensualidades --mes 4 --anio 2026
python manage.py generar_mensualidades  # mes/año actual
```

### 8.4 Documentar uso recurrente

En `README.md` agregar nota:

> **Generar mensualidades cada mes:** ejecutar `python manage.py generar_mensualidades` el primer día de cada mes. Idempotente — si ya existen, no las duplica. En producción puede automatizarse con cron o systemd timer.

### 8.5 Commit

```bash
git add -A
git commit -m "feat(finanzas): management command para generar mensualidades del mes"
```

---

## 9. FASE 5 — Templates

**Tiempo:** 2 horas.

Asume que existe `base.html` con `{% block content %}`. Si no, crear uno básico.

### 9.1 `templates/finanzas/reportar.html`

```html
{% extends 'base.html' %}
{% block content %}
<div class="max-w-2xl mx-auto p-6">
  <h1 class="text-2xl font-bold mb-6">Reportar pago</h1>

  {% if messages %}
    {% for message in messages %}
      <div class="p-3 mb-4 rounded {% if message.tags == 'error' %}bg-red-100 text-red-800{% else %}bg-green-100 text-green-800{% endif %}">
        {{ message }}
      </div>
    {% endfor %}
  {% endif %}

  <form method="post" enctype="multipart/form-data" class="space-y-4">
    {% csrf_token %}

    <div class="border rounded p-4 bg-blue-50">
      <label class="block text-sm font-medium mb-2">Mensualidades a cubrir</label>
      {% if form.mensualidades.field.queryset %}
        <div class="space-y-1 max-h-48 overflow-y-auto">
          {% for choice in form.mensualidades %}
            <label class="flex items-center text-sm">
              {{ choice.tag }}
              <span class="ml-2">{{ choice.choice_label }}</span>
            </label>
          {% endfor %}
        </div>
      {% else %}
        <p class="text-sm text-gray-600">No tienes mensualidades pendientes.</p>
      {% endif %}
      <p class="text-xs text-gray-500 mt-2">{{ form.mensualidades.help_text }}</p>
    </div>

    {% for field in form %}
      {% if field.name != 'mensualidades' %}
        <div>
          <label class="block text-sm font-medium mb-1">{{ field.label }}</label>
          {{ field }}
          {% if field.help_text %}
            <p class="text-xs text-gray-500 mt-1">{{ field.help_text }}</p>
          {% endif %}
          {% if field.errors %}
            <p class="text-xs text-red-600 mt-1">{{ field.errors|join:", " }}</p>
          {% endif %}
        </div>
      {% endif %}
    {% endfor %}

    <button type="submit" class="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
      Enviar pago
    </button>
  </form>
</div>
{% endblock %}
```

### 9.2 `templates/finanzas/mis_pagos.html`

```html
{% extends 'base.html' %}
{% block content %}
<div class="max-w-5xl mx-auto p-6">
  <div class="flex justify-between items-center mb-6">
    <h1 class="text-2xl font-bold">Mis pagos</h1>
    <a href="{% url 'finanzas:reportar' %}" class="bg-blue-600 text-white px-4 py-2 rounded">+ Reportar pago</a>
  </div>

  {% if mensualidades_pendientes %}
    <div class="border rounded p-4 mb-6 bg-yellow-50">
      <h2 class="font-bold mb-2">Mensualidades pendientes</h2>
      <ul class="text-sm space-y-1">
        {% for m in mensualidades_pendientes %}
          <li class="flex justify-between {% if m.vencida %}text-red-700{% endif %}">
            <span>{{ m.atleta.nombres }} {{ m.atleta.apellidos }} — {{ m.etiqueta_periodo }}</span>
            <span>${{ m.monto_usd }} {% if m.vencida %}(VENCIDA){% endif %}</span>
          </li>
        {% endfor %}
      </ul>
    </div>
  {% endif %}

  <table class="w-full text-sm border">
    <thead class="bg-gray-100">
      <tr>
        <th class="p-2 text-left">#</th>
        <th class="p-2 text-left">Concepto</th>
        <th class="p-2 text-left">Método</th>
        <th class="p-2 text-right">Monto Bs</th>
        <th class="p-2 text-right">USD</th>
        <th class="p-2 text-left">Fecha</th>
        <th class="p-2 text-left">Estado</th>
      </tr>
    </thead>
    <tbody>
      {% for p in pagos %}
        <tr class="border-t">
          <td class="p-2">{{ p.id }}</td>
          <td class="p-2">{{ p.concepto|truncatechars:50 }}</td>
          <td class="p-2">{{ p.get_metodo_display }}</td>
          <td class="p-2 text-right">{{ p.monto_bs }}</td>
          <td class="p-2 text-right">{{ p.monto_usd|default:"—" }}</td>
          <td class="p-2">{{ p.fecha_pago }}</td>
          <td class="p-2">
            {% if p.estado == 'APROBADO' %}<span class="px-2 py-1 bg-green-100 text-green-800 rounded text-xs">Aprobado</span>
            {% elif p.estado == 'RECHAZADO' %}<span class="px-2 py-1 bg-red-100 text-red-800 rounded text-xs">Rechazado</span>
            {% else %}<span class="px-2 py-1 bg-yellow-100 text-yellow-800 rounded text-xs">Pendiente</span>
            {% endif %}
          </td>
        </tr>
      {% empty %}
        <tr><td colspan="7" class="p-4 text-center text-gray-500">No hay pagos reportados.</td></tr>
      {% endfor %}
    </tbody>
  </table>
</div>
{% endblock %}
```

### 9.3 `templates/finanzas/bandeja.html`

```html
{% extends 'base.html' %}
{% block content %}
<div class="max-w-7xl mx-auto p-6">
  <h1 class="text-2xl font-bold mb-6">Bandeja de pagos</h1>

  <div class="flex gap-2 mb-4">
    <a href="?estado=PENDIENTE" class="px-3 py-1 rounded {% if estado_actual == 'PENDIENTE' %}bg-blue-600 text-white{% else %}bg-gray-200{% endif %}">Pendientes</a>
    <a href="?estado=APROBADO" class="px-3 py-1 rounded {% if estado_actual == 'APROBADO' %}bg-blue-600 text-white{% else %}bg-gray-200{% endif %}">Aprobados</a>
    <a href="?estado=RECHAZADO" class="px-3 py-1 rounded {% if estado_actual == 'RECHAZADO' %}bg-blue-600 text-white{% else %}bg-gray-200{% endif %}">Rechazados</a>
    <a href="?estado=TODOS" class="px-3 py-1 rounded {% if estado_actual == 'TODOS' %}bg-blue-600 text-white{% else %}bg-gray-200{% endif %}">Todos</a>
  </div>

  <table class="w-full text-sm border">
    <thead class="bg-gray-100">
      <tr>
        <th class="p-2 text-left">#</th>
        <th class="p-2 text-left">Representante</th>
        <th class="p-2 text-left">Concepto</th>
        <th class="p-2 text-left">Método</th>
        <th class="p-2 text-left">Banco</th>
        <th class="p-2 text-left">Ref.</th>
        <th class="p-2 text-right">Monto Bs</th>
        <th class="p-2 text-left">Fecha</th>
        <th class="p-2 text-left">Estado</th>
        <th class="p-2"></th>
      </tr>
    </thead>
    <tbody>
      {% for p in pagos %}
        <tr class="border-t hover:bg-gray-50">
          <td class="p-2">{{ p.id }}</td>
          <td class="p-2">{{ p.representante.nombres }} {{ p.representante.apellidos }}</td>
          <td class="p-2">{{ p.concepto|truncatechars:40 }}</td>
          <td class="p-2">{{ p.get_metodo_display }}</td>
          <td class="p-2">{{ p.get_banco_emisor_display }}</td>
          <td class="p-2 font-mono text-xs">{{ p.referencia }}</td>
          <td class="p-2 text-right">{{ p.monto_bs }}</td>
          <td class="p-2">{{ p.fecha_pago }}</td>
          <td class="p-2">
            {% if p.estado == 'APROBADO' %}<span class="px-2 py-1 bg-green-100 text-green-800 rounded text-xs">✓</span>
            {% elif p.estado == 'RECHAZADO' %}<span class="px-2 py-1 bg-red-100 text-red-800 rounded text-xs">✗</span>
            {% else %}<span class="px-2 py-1 bg-yellow-100 text-yellow-800 rounded text-xs">⏳</span>
            {% endif %}
          </td>
          <td class="p-2">
            <a href="{% url 'finanzas:detalle' p.id %}" class="text-blue-600 hover:underline">Ver</a>
          </td>
        </tr>
      {% empty %}
        <tr><td colspan="10" class="p-4 text-center text-gray-500">Sin pagos.</td></tr>
      {% endfor %}
    </tbody>
  </table>
</div>
{% endblock %}
```

### 9.4 `templates/finanzas/detalle.html`

```html
{% extends 'base.html' %}
{% block content %}
<div class="max-w-6xl mx-auto p-6">
  <a href="{% url 'finanzas:bandeja' %}" class="text-blue-600 hover:underline mb-4 inline-block">← Volver a bandeja</a>
  <h1 class="text-2xl font-bold mb-6">Pago #{{ pago.id }}</h1>

  <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
    <!-- Comprobante -->
    <div class="border rounded p-4">
      <h2 class="font-bold mb-3">Comprobante</h2>
      {% with ext=pago.comprobante.url|lower %}
        {% if '.pdf' in ext %}
          <embed src="{{ pago.comprobante.url }}" type="application/pdf" class="w-full h-96" />
          <a href="{{ pago.comprobante.url }}" target="_blank" class="text-blue-600 hover:underline mt-2 inline-block">Abrir PDF</a>
        {% else %}
          <img src="{{ pago.comprobante.url }}" class="w-full border" alt="Comprobante" />
        {% endif %}
      {% endwith %}
      <p class="text-xs text-gray-500 mt-2">Hash: {{ pago.comprobante_hash|slice:":16" }}…</p>
    </div>

    <!-- Datos -->
    <div class="space-y-4">
      <div class="border rounded p-4">
        <h2 class="font-bold mb-3">Datos del pago</h2>
        <dl class="text-sm space-y-1">
          <div class="flex justify-between"><dt class="text-gray-600">Representante:</dt><dd>{{ pago.representante.nombres }} {{ pago.representante.apellidos }}</dd></div>
          <div class="flex justify-between"><dt class="text-gray-600">Cédula:</dt><dd>{{ pago.representante.cedula_identidad }}</dd></div>
          <div class="flex justify-between"><dt class="text-gray-600">Concepto:</dt><dd>{{ pago.concepto }}</dd></div>
          <div class="flex justify-between"><dt class="text-gray-600">Método:</dt><dd>{{ pago.get_metodo_display }}</dd></div>
          <div class="flex justify-between"><dt class="text-gray-600">Banco:</dt><dd>{{ pago.get_banco_emisor_display|default:"—" }}</dd></div>
          <div class="flex justify-between"><dt class="text-gray-600">Referencia:</dt><dd class="font-mono">{{ pago.referencia|default:"—" }}</dd></div>
          <div class="flex justify-between"><dt class="text-gray-600">Monto Bs:</dt><dd class="font-bold">{{ pago.monto_bs }}</dd></div>
          <div class="flex justify-between"><dt class="text-gray-600">Tasa BCV:</dt><dd>{{ pago.tasa_bcv|default:"Pendiente" }}</dd></div>
          <div class="flex justify-between"><dt class="text-gray-600">Monto USD:</dt><dd class="font-bold">{{ pago.monto_usd|default:"—" }}</dd></div>
          <div class="flex justify-between"><dt class="text-gray-600">Fecha pago:</dt><dd>{{ pago.fecha_pago }}</dd></div>
          <div class="flex justify-between"><dt class="text-gray-600">Estado:</dt><dd class="font-bold">{{ pago.get_estado_display }}</dd></div>
          {% if pago.revisado_por %}
            <div class="flex justify-between"><dt class="text-gray-600">Revisado por:</dt><dd>{{ pago.revisado_por }}</dd></div>
            <div class="flex justify-between"><dt class="text-gray-600">Revisado el:</dt><dd>{{ pago.revisado_en }}</dd></div>
          {% endif %}
          {% if pago.motivo_rechazo %}
            <div class="mt-2 p-2 bg-red-50 text-red-800 rounded"><strong>Motivo:</strong> {{ pago.motivo_rechazo }}</div>
          {% endif %}
        </dl>
      </div>

      {% if pago.mensualidades_cubiertas.all %}
        <div class="border rounded p-4">
          <h3 class="font-bold mb-2">Mensualidades cubiertas</h3>
          <ul class="text-sm space-y-1">
            {% for m in pago.mensualidades_cubiertas.all %}
              <li>{{ m.atleta }} — {{ m.etiqueta_periodo }} ({{ m.monto_usd }} USD) {% if m.pagada %}<span class="text-green-700">✓</span>{% endif %}</li>
            {% endfor %}
          </ul>
        </div>
      {% endif %}

      <div class="border rounded p-4 bg-gray-50">
        <h3 class="font-bold mb-2">Historial</h3>
        <ul class="text-xs space-y-1 max-h-48 overflow-y-auto">
          {% for log in audit_log %}
            <li>
              <span class="text-gray-500">{{ log.timestamp|date:"d/m/Y H:i" }}</span>
              <strong>{{ log.get_accion_display }}</strong>
              {% if log.actor %}por {{ log.actor }}{% endif %}
              {% if log.estado_anterior %}({{ log.estado_anterior }} → {{ log.estado_nuevo }}){% endif %}
            </li>
          {% empty %}
            <li class="text-gray-500">Sin historial.</li>
          {% endfor %}
        </ul>
      </div>

      {% if pago.estado == 'PENDIENTE' %}
        <div class="border rounded p-4 bg-green-50">
          <h3 class="font-bold mb-2">Aprobar</h3>
          <form method="post" action="{% url 'finanzas:aprobar' pago.id %}" class="space-y-2">
            {% csrf_token %}
            <label class="block text-sm">Tasa BCV (Bs por USD)</label>
            {{ aprobar_form.tasa_bcv }}
            <button class="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700">Aprobar pago</button>
          </form>
        </div>

        <div class="border rounded p-4 bg-red-50">
          <h3 class="font-bold mb-2">Rechazar</h3>
          <form method="post" action="{% url 'finanzas:rechazar' pago.id %}" class="space-y-2">
            {% csrf_token %}
            <label class="block text-sm">Motivo</label>
            {{ rechazar_form.motivo }}
            <button class="bg-red-600 text-white px-4 py-2 rounded hover:bg-red-700">Rechazar pago</button>
          </form>
        </div>
      {% endif %}
    </div>
  </div>
</div>
{% endblock %}
```

### 9.5 Commit

```bash
git add -A
git commit -m "feat(finanzas): templates con mensualidades, audit log e historial"
```

---

## 10. FASE 6 — Telegram bot

**Tiempo:** 1.5 horas.

### 10.1 Crear el bot

1. Telegram → buscar **@BotFather**.
2. `/newbot` → seguir instrucciones → guardar token.
3. Agregar al `.env`:
```
TELEGRAM_BOT_TOKEN=123456:ABC-DEF...
```

### 10.2 Verificar `requests` en `requirements.txt` y `django-ratelimit`

```
requests>=2.31.0
django-ratelimit>=4.1.0
```

```bash
pip install -r requirements.txt
```

### 10.3 Probar envío manual

```bash
python manage.py shell
>>> from finanzas.telegram_bot import enviar_mensaje
>>> enviar_mensaje(TU_CHAT_ID, 'Prueba')
```

Obtener tu `chat_id` propio escribiéndole a `@userinfobot`.

### 10.4 Asociación representante ↔ chat_id

**Opción A (con HTTPS):** registrar webhook:
```bash
curl "https://api.telegram.org/bot<TOKEN>/setWebhook?url=https://tu-dominio.com/finanzas/telegram/webhook/"
```
El representante envía `/start SU_CEDULA` al bot.

**Opción B (sin HTTPS, manual):**
1. Representante escribe al bot.
2. Admin abre `https://api.telegram.org/bot<TOKEN>/getUpdates`.
3. Localiza `chat_id` y lo pega en Django admin.

### 10.5 Logging en `settings.py`

```python
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {'class': 'logging.StreamHandler'},
    },
    'loggers': {
        'finanzas.telegram_bot': {
            'handlers': ['console'],
            'level': 'WARNING',
        },
    },
}
```

### 10.6 Commit

```bash
git add -A
git commit -m "feat(finanzas): integración Telegram bot funcional"
```

---

## 11. FASE 7 — QA

**Tiempo:** 2 horas.

### 11.1 Tests funcionales (manuales)

- [ ] Crear superusuario (si no existe, el actual es FDM y contraseña FDM).
- [ ] Crear `Categoria` (si no existe) en admin.
- [ ] Crear `Representante` y asociarlo al usuario vía campo `usuario`.
- [ ] Crear `Atleta` activo asociado al representante.
- [ ] Correr `python manage.py generar_mensualidades`.
- [ ] Verificar que aparecen mensualidades en admin.
- [ ] Login con representante.
- [ ] Visitar `/finanzas/mis-pagos/` — ver mensualidades pendientes.
- [ ] Visitar `/finanzas/reportar/` — ver checkboxes de mensualidades.
- [ ] Reportar pago seleccionando 1 mensualidad.
- [ ] Verificar que `concepto` se construye automáticamente.
- [ ] Intentar reportar mismo comprobante — rechazado por hash.
- [ ] Intentar reportar misma referencia + banco — rechazado por constraint.
- [ ] Reportar 6 pagos seguidos en 1 hora — el 6º debe ser bloqueado por rate limit (429).
- [ ] Login con superusuario.
- [ ] Visitar `/finanzas/admin/bandeja/`.
- [ ] Click "Ver" — ver comprobante, datos, mensualidades vinculadas, historial vacío excepto "CREADO".
- [ ] Aprobar con tasa BCV.
- [ ] Verificar: `monto_usd` calculado, mensualidad marcada como `pagada=True`, audit log con entradas APROBADO y MENSUALIDADES_VINCULADAS.
- [ ] Verificar mensaje en Telegram (si configurado).
- [ ] Reportar otro pago, rechazarlo con motivo.
- [ ] Verificar: mensualidades vinculadas se desvinculan (vuelven a estar disponibles), audit log con RECHAZADO.
- [ ] Filtros de bandeja funcionan.
- [ ] Cero errores 500.

### 11.2 Mejoras UX mínimas

- [ ] Mensajes flash visibles en `base.html`.
- [ ] Estilos Tailwind aplicados a inputs (puede requerir clases adicionales en `attrs`).
- [ ] Link a "Reportar pago" en menú principal del representante.
- [ ] Link a "Bandeja de pagos" en menú admin.

### 11.3 Commit

```bash
git add -A
git commit -m "chore(finanzas): QA y mejoras UX MVP"
```

---

## 12. FASE 8 — Documentación y cierre

**Tiempo:** 45 minutos.

### 12.1 Actualizar `README.md`

Agregar sección:

```markdown
## Módulo de Pagos

### Variables de entorno requeridas
- `TELEGRAM_BOT_TOKEN` — obtener vía @BotFather en Telegram

### Comandos importantes
- `python manage.py generar_mensualidades` — genera mensualidades del mes actual
- `python manage.py generar_mensualidades --mes 4 --anio 2026` — mes específico
- `python manage.py createcachetable` — crea tabla de cache para rate limiting

### Asociación de representante a Telegram
Opción manual: el admin pega el `chat_id` desde Django admin.
Opción webhook: configurar webhook con HTTPS público y representante envía `/start CEDULA`.

### Permisos
Solo `is_staff` o miembros del grupo `Tesoreria` acceden a la bandeja administrativa.
```

### 12.2 Pull request

Mensaje sugerido:

```
feat: módulo de pagos venezolanos MVP + limpieza logística

## Cambios
- Eliminado módulo `logistica` obsoleto
- Modelos Pago, Mensualidad y PagoAuditLog
- Bandeja administrativa con flujo aprobar/rechazar
- Selección de mensualidades a cubrir desde el form de reporte
- Audit log inmutable con historial completo
- Notificaciones vía Telegram bot
- Rate limiting en endpoints sensibles
- Constraint DB para referencias bancarias duplicadas
- Hash SHA-256 anti-comprobantes duplicados
- Conversión automática Bs → USD al aprobar
- Management command para generar mensualidades

## Pendiente V2
- Generación recibo PDF
```

---

## 13. Trampas conocidas

1. **No implementar Celery/Django-Q.** Todo síncrono.
2. **No implementar OCR.** Diferido a V2.
3. **No implementar scraper BCV.** Manual al aprobar.
4. **No pelear con permisos granulares.** `is_staff` o grupo `Tesoreria`.
5. **No implementar storage S3.** Filesystem local.
6. **No generar recibo PDF.** WeasyPrint disponible para V2.
7. **No usar `python-magic`.** Validación por extensión.
8. **Si Telegram webhook requiere HTTPS y no lo tienes:** atajo manual (Opción B en Fase 6).
9. **Si la migración del `Pago` viejo falla:** eliminar migraciones y regenerar.
10. **`request.user.representante`:** verificar `related_name='representante'`.
11. **NO duplicar `MEDIA_URL`/`MEDIA_ROOT`** — ya existen.
12. **NO duplicar bloque `static()`** — ya existe.
13. **NO eliminar `Patrocinante` y `Aporte`** — preservar.
14. **`createcachetable` antes de probar rate limiting** o fallará silenciosamente.
15. **Al rechazar un pago, las mensualidades se desvinculan** (vuelven a `pago=None`) para que el representante pueda reportarlas en otro pago.
16. **El management command es idempotente** — `get_or_create` evita duplicados.
17. **AuditLog NUNCA se modifica desde código de aplicación**, solo se crea. Admin ya lo bloquea.

---

## 14. Decisiones técnicas resueltas

| Decisión | Resolución |
|---|---|
| Tasa BCV | Manual al aprobar |
| OCR | Diferido a V2 |
| Mensualidades | **Modelo separado, generación vía management command idempotente** |
| Audit log | **Tabla separada, inmutable, vía helper `registrar_audit()`** |
| Storage | Filesystem local |
| Notificaciones | Telegram bot únicamente |
| Token Telegram | Cédula del representante |
| Permisos | `is_staff` o grupo `Tesoreria` |
| Async tasks | Síncrono |
| Recibo aprobación | Telegram texto plano |
| **Rate limiting** | **`django-ratelimit` con cache de DB. 5 reportes/h por usuario, 30 aprobaciones/min admin, 60 webhooks/min IP** |
| Validación MIME | Por extensión |
| Vinculación mensualidad-pago | Al reportar (FK), confirmada al aprobar (`pagada=True`) |
| Rechazo | Desvincula mensualidades (vuelven disponibles) |

---

## 15. Métricas de éxito

1. ✅ Módulo `logistica` removido, servidor levanta sin errores.
2. ✅ Representante puede ver mensualidades pendientes en menos de 5 segundos.
3. ✅ Reportar pago con selección de mensualidades en menos de 2 minutos.
4. ✅ Admin aprueba/rechaza en menos de 60 segundos.
5. ✅ Mensualidades cubiertas se marcan `pagada=True` al aprobar.
6. ✅ Mensualidades se liberan al rechazar.
7. ✅ Comprobantes y referencias duplicadas rechazados automáticamente.
8. ✅ Rate limiting bloquea exceso de requests con HTTP 429.
9. ✅ Notificación Telegram en menos de 5 segundos tras decisión admin.
10. ✅ Audit log registra creación, aprobación y rechazo con actor y timestamp.
11. ✅ Admin puede consultar histórico completo de cualquier pago.
12. ✅ Cero errores 500 en flujo principal.
13. ✅ `generar_mensualidades` es idempotente.

---

## 16. Resumen del plan

| Fase | Tarea | Tiempo | Commit |
|---|---|---|---|
| **0** | Eliminar logística | 30 min | `chore: eliminar módulo logística obsoleto` |
| **1** | Modelos + admin | 3h | `feat(finanzas): modelos Pago, Mensualidad y PagoAuditLog` |
| **2** | Forms + URLs + cache | 45 min | `feat(finanzas): forms con selección de mensualidades + cache` |
| **3** | Vistas con rate limit y audit | 2h | `feat(finanzas): vistas con rate limiting, audit log y vinculación` |
| **4** | Management command | 1h | `feat(finanzas): command generar_mensualidades` |
| **5** | Templates | 2h | `feat(finanzas): templates con mensualidades, audit log e historial` |
| **6** | Telegram bot | 1.5h | `feat(finanzas): integración Telegram bot funcional` |
| **7** | QA | 2h | `chore(finanzas): QA y mejoras UX MVP` |
| **8** | Docs + PR | 45 min | PR a rama principal |
| **TOTAL** | | **~13.5h** | |

**Distribución sugerida:**
- **Día 1 (8h):** Fases 0, 1, 2, 3.
- **Día 2 (5.5h):** Fases 4, 5, 6, 7, 8.

---

## 17. Roadmap V2

- OCR con Tesseract.
- Scraper automático BCV.
- Generación recibo PDF con WeasyPrint.
- Storage S3-compatible.
- Validación MIME real con `python-magic`.
- Token aleatorio quemable Telegram.
- Notificaciones de mensualidad próxima a vencer.
- Dashboard financiero con métricas.
- Integración con módulo deportivo: bloquear acceso si hay mensualidades vencidas.
- Riesgo score y auto-aprobación.
- Pagos parciales / planes de pago.

---

**Fin del PRD.**

---