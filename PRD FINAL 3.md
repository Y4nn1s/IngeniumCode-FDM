---

# PRD — Mejoras de Cobertura y Formato (v1.2 — post-DolarAPI)

**Proyecto:** IngeniumCode-FDM
**Rama:** `Módulo-de-Pagos`
**Versión:** 1.2 (parche correctivo, aplicable DESPUÉS de v1.3 DolarAPI)
**Fecha:** 2026-04-29
**Plazo estimado:** 2-3 horas

---

## 0. Instrucciones para la IA ejecutora

Este PRD corrige bugs de lógica financiera y formato de presentación en el módulo de pagos. **Asume que el PRD v1.3 (DolarAPI) ya fue implementado.**

NO reescribe arquitectura. Son cambios quirúrgicos sobre archivos específicos. Trabaja sobre la rama `Módulo-de-Pagos`. Ejecuta las fases en orden. Haz commit después de cada fase.

---

## 1. Bugs detectados

### Bug 1 — Pago insuficiente solventa mensualidad (CRÍTICO)

**Síntoma reproducido:**
- Atleta "Yannisito Jr." debe mensualidad de Enero 2026 por **15 USD**.
- Representante reporta pago de **900 Bs** con tasa BCV **486** = **1.85 USD**.
- Admin aprueba el pago.
- La mensualidad queda marcada como `pagada=True` y el atleta aparece como solvente.

**Mecanismo:** en `finanzas/views.py`, función `aprobar()`, el bloque que marca mensualidades como pagadas no valida que el monto USD cubra la suma esperada:

```python
mensualidades = pago.mensualidades_cubiertas.all()
for m in mensualidades:
    m.pagada = True   # ← marca sin validar
    m.save()
```

**Impacto:** financiero directo. Pérdida de ingresos al considerar solventes a representantes que pagaron una fracción.

### Bug 2 — Decimales sin redondear en notificación Telegram

**Síntoma:**
```
✅ Tu pago #1 de 900.00 Bs (1.851851851851851851851851852 USD) fue APROBADO.
```

**Mecanismo:** en `finanzas/models.py`, `save()`:

```python
self.monto_usd = self.monto_bs / self.tasa_bcv
```

La división de Decimals produce precisión completa (28 dígitos). El campo tiene `decimal_places=2`, pero ese redondeo solo se aplica al guardar en Postgres — el objeto en memoria tiene el valor sin redondear, y el f-string del mensaje Telegram interpola lo que está en memoria.

**Impacto:** experiencia de usuario.

### Bug 3 — Formato sin localización venezolana

**Síntoma:** los montos se muestran como `900.00 Bs` y `1.85 USD` con punto decimal inglés. En Venezuela el estándar es `Bs 900,00` y `$ 1,85` con coma decimal y punto de miles (`Bs 1.250,00`).

**Impacto:** menor, pero el sistema se siente extranjero.

---

## 2. Alcance

### Dentro del alcance

- ✅ Validar que el monto USD del pago cubra la suma USD de las mensualidades vinculadas antes de aprobarlas.
- ✅ Bloquear aprobación si no cubre, con mensaje claro al admin.
- ✅ Redondear `monto_usd` a 2 decimales explícitamente con `ROUND_HALF_UP`.
- ✅ Formatear mensajes Telegram con localización venezolana (Bs y $ con coma decimal).
- ✅ Filtros de plantilla `bs` y `usd` aplicados en mis_pagos, bandeja, detalle.
- ✅ Mostrar al representante el **total USD** de las mensualidades seleccionadas en el form.
- ✅ Mostrar al admin la **comparación**: total esperado vs. monto recibido en el detalle.

### Fuera del alcance

- ❌ Pagos parciales que cubren porcentaje de mensualidad.
- ❌ Sistema de "saldo a favor" si el representante paga de más.
- ❌ Cambio de tasa BCV una vez aprobado.
- ❌ Reapertura de pagos aprobados.

---

## 3. Decisión de diseño — política de cobertura

Cuando el admin va a aprobar un pago con mensualidades vinculadas, el sistema compara:

```
total_esperado_usd = suma de monto_usd de mensualidades vinculadas
monto_recibido_usd = monto_bs / tasa_bcv (con tasa ingresada al aprobar)
```

| Escenario | Condición | Acción |
|---|---|---|
| **Cobertura completa** | `monto_recibido_usd >= total_esperado_usd - tolerancia` | Aprobar. Marcar mensualidades como `pagada=True`. |
| **Cobertura insuficiente** | `monto_recibido_usd < total_esperado_usd - tolerancia` | Bloquear. Mostrar diferencia al admin. |
| **Sin mensualidades vinculadas** | `mensualidades.count() == 0` | Aprobar sin validación de cobertura. |

**Tolerancia:** se permite una diferencia de hasta **0.50 USD** por debajo del total esperado, para absorber redondeos y diferencias mínimas de tasa. Constante `TOLERANCIA_COBERTURA_USD = Decimal('0.50')` en `models.py`.

> **Justificación de la tolerancia:** la tasa BCV cambia día a día. Si la mensualidad se generó con tasa 480 y el pago entra con tasa 486, la diferencia de céntimos no debe bloquear la aprobación. Con DolarAPI ya integrado (v1.3), la tasa pre-cargada es la del día del pago, lo que minimiza estos desfases — pero la tolerancia sigue siendo útil para casos edge.

---

## 4. FASE 1 — Corrección de redondeo de `monto_usd`

**Archivo:** `finanzas/models.py`
**Tiempo:** 15 min.

### 4.1 Modificar el `save()` del modelo `Pago`

Buscar:

```python
def save(self, *args, **kwargs):
    if self.comprobante and not self.comprobante_hash:
        self.comprobante_hash = self._calcular_hash()
    if self.monto_bs and self.tasa_bcv:
        self.monto_usd = self.monto_bs / self.tasa_bcv
    super().save(*args, **kwargs)
```

Reemplazar por:

```python
def save(self, *args, **kwargs):
    if self.comprobante and not self.comprobante_hash:
        self.comprobante_hash = self._calcular_hash()
    if self.monto_bs and self.tasa_bcv:
        # Redondeo a 2 decimales con HALF_UP (estándar contable)
        self.monto_usd = (self.monto_bs / self.tasa_bcv).quantize(
            Decimal('0.01'), rounding=ROUND_HALF_UP
        )
    super().save(*args, **kwargs)
```

### 4.2 Actualizar import al tope del archivo

Buscar:

```python
from decimal import Decimal
```

Reemplazar por:

```python
from decimal import Decimal, ROUND_HALF_UP
```

### 4.3 Agregar la constante de tolerancia

Después del bloque de choices, antes del modelo `TasaBCV` (que ya existe desde v1.3):

```python
# === Constantes de negocio ===
TOLERANCIA_COBERTURA_USD = Decimal('0.50')
```

### 4.4 Commit

```bash
git add finanzas/models.py
git commit -m "fix(finanzas): redondear monto_usd a 2 decimales con HALF_UP"
```

---

## 5. FASE 2 — Validación de cobertura al aprobar

**Archivo:** `finanzas/views.py`
**Tiempo:** 30 min.

### 5.1 Imports al tope

Verificar que estén presentes (algunos ya pueden estarlo por v1.3):

```python
from decimal import Decimal, ROUND_HALF_UP
from .models import Pago, Mensualidad, PagoAuditLog, TOLERANCIA_COBERTURA_USD
```

### 5.2 Reemplazar la función `aprobar()` completa

Buscar la función `aprobar()` y reemplazarla por:

```python
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
            tasa = form.cleaned_data['tasa_bcv']

            # Calcular monto USD que se obtendría con esta tasa
            monto_usd_calculado = (pago.monto_bs / tasa).quantize(
                Decimal('0.01'), rounding=ROUND_HALF_UP
            )

            # Validar cobertura contra mensualidades vinculadas
            mensualidades = pago.mensualidades_cubiertas.all()
            total_esperado = sum(
                (m.monto_usd for m in mensualidades),
                Decimal('0.00')
            )

            if mensualidades.exists() and monto_usd_calculado < (total_esperado - TOLERANCIA_COBERTURA_USD):
                faltante = (total_esperado - monto_usd_calculado).quantize(Decimal('0.01'))
                messages.error(
                    request,
                    f'Cobertura insuficiente. Pago = {monto_usd_calculado} USD, '
                    f'mensualidades = {total_esperado} USD. '
                    f'Faltan {faltante} USD. Rechaza el pago o solicita complemento.'
                )
                return redirect('finanzas:detalle', pk=pk)

            with transaction.atomic():
                estado_anterior = pago.estado
                pago.tasa_bcv = tasa
                pago.estado = 'APROBADO'
                pago.revisado_por = request.user
                pago.revisado_en = timezone.now()
                pago.save()

                # Marcar mensualidades vinculadas como pagadas (cobertura validada)
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
                        'total_esperado_usd': str(total_esperado),
                        'mensualidades_pagadas': [m.id for m in mensualidades],
                    }
                )

                if mensualidades.exists():
                    pago.registrar_audit(
                        accion='MENSUALIDADES_VINCULADAS',
                        actor=request.user,
                        detalles={'count': mensualidades.count()}
                    )

            from .telegram_bot import notificar_pago_aprobado
            notificar_pago_aprobado(pago)

            messages.success(request, f'Pago #{pago.id} aprobado.')
        else:
            messages.error(request, 'Tasa BCV inválida.')

    return redirect('finanzas:bandeja')
```

### 5.3 Commit

```bash
git add finanzas/views.py
git commit -m "fix(finanzas): bloquear aprobación si pago no cubre mensualidades vinculadas"
```

---

## 6. FASE 3 — Notificación Telegram con formato venezolano

**Archivo:** `finanzas/telegram_bot.py`
**Tiempo:** 30 min.

### 6.1 Agregar helpers de formato al tope del archivo

Después de los imports existentes:

```python
from decimal import Decimal


def formato_bs(valor):
    """Formatea un Decimal como '1.250,00 Bs' (estilo venezolano)."""
    if valor is None:
        return '—'
    s = f'{Decimal(valor):,.2f}'
    s = s.replace(',', 'X').replace('.', ',').replace('X', '.')
    return f'{s} Bs'


def formato_usd(valor):
    """Formatea un Decimal como '$ 15,00' (estilo venezolano)."""
    if valor is None:
        return '—'
    s = f'{Decimal(valor):,.2f}'
    s = s.replace(',', 'X').replace('.', ',').replace('X', '.')
    return f'$ {s}'
```

### 6.2 Agregar funciones específicas de notificación

Al final del archivo:

```python
def notificar_pago_aprobado(pago):
    """Envía mensaje de aprobación con formato localizado."""
    texto = (
        f'✅ Tu pago <b>#{pago.id}</b> fue APROBADO.\n'
        f'Monto: {formato_bs(pago.monto_bs)} ({formato_usd(pago.monto_usd)})\n'
        f'Concepto: {pago.concepto}'
    )
    return notificar_representante(pago.representante, texto)


def notificar_pago_rechazado(pago):
    """Envía mensaje de rechazo con formato localizado."""
    texto = (
        f'❌ Tu pago <b>#{pago.id}</b> fue RECHAZADO.\n'
        f'Monto: {formato_bs(pago.monto_bs)}\n'
        f'Motivo: {pago.motivo_rechazo}'
    )
    return notificar_representante(pago.representante, texto)
```

### 6.3 Actualizar la función `rechazar()` en `views.py`

Buscar en `finanzas/views.py`, dentro de `rechazar()`:

```python
notificar_representante(
    pago.representante,
    f'❌ Tu pago #{pago.id} fue RECHAZADO.\n'
    f'Motivo: {pago.motivo_rechazo}'
)
```

Reemplazar por:

```python
from .telegram_bot import notificar_pago_rechazado
notificar_pago_rechazado(pago)
```

### 6.4 Probar manualmente

```bash
python manage.py shell
```

```python
from finanzas.telegram_bot import formato_bs, formato_usd
from decimal import Decimal
print(formato_bs(Decimal('1250.50')))    # → 1.250,50 Bs
print(formato_bs(Decimal('900.00')))     # → 900,00 Bs
print(formato_usd(Decimal('1.851851')))  # → $ 1,85
print(formato_usd(Decimal('15.00')))     # → $ 15,00
```

### 6.5 Commit

```bash
git add finanzas/telegram_bot.py finanzas/views.py
git commit -m "fix(finanzas): notificaciones Telegram con formato venezolano"
```

---

## 7. FASE 4 — Total esperado en form de reporte

**Archivos:** `finanzas/forms.py`, `templates/finanzas/reportar.html`
**Tiempo:** 30 min.

### 7.1 Modificar `__init__` de `ReportarPagoForm`

En `finanzas/forms.py`, buscar:

```python
def __init__(self, *args, **kwargs):
    representante = kwargs.pop('representante', None)
    super().__init__(*args, **kwargs)
    if representante:
        atletas = representante.atletas.filter(activo=True)
        self.fields['mensualidades'].queryset = Mensualidad.objects.filter(
            atleta__in=atletas, pagada=False
        ).select_related('atleta').order_by('fecha_vencimiento')
```

Reemplazar por:

```python
def __init__(self, *args, **kwargs):
    representante = kwargs.pop('representante', None)
    super().__init__(*args, **kwargs)
    if representante:
        atletas = representante.atletas.filter(activo=True)
        qs = Mensualidad.objects.filter(
            atleta__in=atletas, pagada=False
        ).select_related('atleta').order_by('fecha_vencimiento')
        self.fields['mensualidades'].queryset = qs
        # Etiqueta enriquecida con monto USD
        self.fields['mensualidades'].label_from_instance = (
            lambda m: f"{m.atleta.nombres} {m.atleta.apellidos} — {m.etiqueta_periodo} (${m.monto_usd})"
        )
```

### 7.2 Modificar `templates/finanzas/reportar.html`

Buscar el bloque de mensualidades:

```html
<div class="space-y-1 max-h-48 overflow-y-auto">
  {% for choice in form.mensualidades %}
    <label class="flex items-center text-sm">
      {{ choice.tag }}
      <span class="ml-2">{{ choice.choice_label }}</span>
    </label>
  {% endfor %}
</div>
```

Reemplazar por:

```html
<div class="space-y-1 max-h-48 overflow-y-auto" id="mensualidades-list">
  {% for choice in form.mensualidades %}
    <label class="flex items-center text-sm">
      <input type="checkbox" name="mensualidades" value="{{ choice.choice_value }}" class="mensualidad-check">
      <span class="ml-2">{{ choice.choice_label }}</span>
    </label>
  {% endfor %}
</div>

<div class="mt-3 p-2 bg-blue-100 rounded text-sm font-semibold" id="total-esperado">
  Total seleccionado: $ 0,00
</div>

<script>
  // Mapa id_mensualidad → monto_usd
  const montosMensualidad = {
    {% for m in form.mensualidades.field.queryset %}
      {{ m.id }}: {{ m.monto_usd }}{% if not forloop.last %},{% endif %}
    {% endfor %}
  };

  function actualizarTotal() {
    const checks = document.querySelectorAll('.mensualidad-check:checked');
    let total = 0;
    checks.forEach(c => {
      const id = parseInt(c.value);
      total += parseFloat(montosMensualidad[id] || 0);
    });
    const formateado = total.toFixed(2).replace('.', ',');
    document.getElementById('total-esperado').textContent =
      `Total seleccionado: $ ${formateado}`;
  }

  document.querySelectorAll('.mensualidad-check').forEach(c => {
    c.addEventListener('change', actualizarTotal);
  });
</script>
```

### 7.3 Commit

```bash
git add finanzas/forms.py templates/finanzas/reportar.html
git commit -m "feat(finanzas): mostrar total USD esperado al seleccionar mensualidades"
```

---

## 8. FASE 5 — Comparación de cobertura en detalle admin

**Archivos:** `finanzas/views.py`, `templates/finanzas/detalle.html`
**Tiempo:** 20 min.

> **Nota:** la vista `detalle_admin` ya fue modificada en v1.3 para pre-cargar la tasa. Aquí solo se agrega `total_esperado_usd` al contexto si no estaba ya, y se ajusta el template.

### 8.1 Verificar `detalle_admin` en `views.py`

La función debería verse así después de v1.3 + v1.2:

```python
@user_passes_test(es_admin)
def detalle_admin(request, pk):
    pago = get_object_or_404(Pago, pk=pk)
    audit = pago.audit_log.all()[:20]
    mensualidades = pago.mensualidades_cubiertas.all()
    total_esperado_usd = sum(
        (m.monto_usd for m in mensualidades),
        Decimal('0.00')
    )

    # Pre-cargar tasa BCV (de v1.3)
    tasa_sugerida = None
    fuente_tasa = None
    if pago.estado == 'PENDIENTE':
        from finanzas.services.tasa_bcv import obtener_tasa
        tasa_sugerida = obtener_tasa(pago.fecha_pago)
        if tasa_sugerida is not None:
            from .models import TasaBCV
            cache_obj = TasaBCV.objects.filter(fecha=pago.fecha_pago).first()
            fuente_tasa = cache_obj.fuente if cache_obj else 'dolarapi'

    aprobar_form = AprobarPagoForm(
        initial={'tasa_bcv': tasa_sugerida} if tasa_sugerida else None
    )

    return render(request, 'finanzas/detalle.html', {
        'pago': pago,
        'audit_log': audit,
        'aprobar_form': aprobar_form,
        'rechazar_form': RechazarPagoForm(),
        'total_esperado_usd': total_esperado_usd,
        'tasa_sugerida': tasa_sugerida,
        'fuente_tasa': fuente_tasa,
    })
```

Si `total_esperado_usd` ya estaba en el contexto desde v1.3, no hay nada que cambiar aquí. Si no estaba, agregarlo.

### 8.2 Modificar `templates/finanzas/detalle.html`

Buscar el bloque que muestra "Mensualidades cubiertas":

```html
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
```

Reemplazar por:

```html
{% if pago.mensualidades_cubiertas.all %}
  <div class="border rounded p-4">
    <h3 class="font-bold mb-2">Mensualidades vinculadas</h3>
    <ul class="text-sm space-y-1">
      {% for m in pago.mensualidades_cubiertas.all %}
        <li>{{ m.atleta }} — {{ m.etiqueta_periodo }} (${{ m.monto_usd }}) {% if m.pagada %}<span class="text-green-700">✓ pagada</span>{% endif %}</li>
      {% endfor %}
    </ul>

    {% if pago.estado == 'PENDIENTE' %}
      <div class="mt-3 p-3 rounded text-sm
        {% if pago.monto_usd and pago.monto_usd < total_esperado_usd %}bg-red-50 text-red-800
        {% else %}bg-blue-50 text-blue-800{% endif %}">
        <div>Total esperado: <strong>${{ total_esperado_usd }}</strong></div>
        <div>Monto reportado: <strong>${{ pago.monto_usd|default:"— (falta tasa BCV)" }}</strong></div>
        {% if pago.monto_usd and pago.monto_usd < total_esperado_usd %}
          <div class="mt-1">⚠️ El pago no cubre el total. Bloqueado para aprobación.</div>
        {% endif %}
      </div>
    {% endif %}
  </div>
{% endif %}
```

### 8.3 Commit

```bash
git add finanzas/views.py templates/finanzas/detalle.html
git commit -m "feat(finanzas): mostrar comparación cobertura en detalle de pago"
```

---

## 9. FASE 6 — Filtros de plantilla para formato venezolano

**Archivos nuevos:** `finanzas/templatetags/__init__.py`, `finanzas/templatetags/finanzas_filters.py`
**Tiempo:** 20 min.

### 9.1 Crear estructura

```bash
mkdir -p finanzas/templatetags
touch finanzas/templatetags/__init__.py
```

### 9.2 Crear `finanzas/templatetags/finanzas_filters.py`

```python
from decimal import Decimal
from django import template

register = template.Library()


def _formato_ve(valor):
    """Formatea Decimal como string '1.250,50' (estilo venezolano)."""
    if valor is None or valor == '':
        return '—'
    try:
        s = f'{Decimal(valor):,.2f}'
        return s.replace(',', 'X').replace('.', ',').replace('X', '.')
    except Exception:
        return str(valor)


@register.filter
def bs(valor):
    """Uso: {{ pago.monto_bs|bs }} → '900,00 Bs'"""
    return f'{_formato_ve(valor)} Bs'


@register.filter
def usd(valor):
    """Uso: {{ pago.monto_usd|usd }} → '$ 1,85'"""
    return f'$ {_formato_ve(valor)}'
```

### 9.3 Aplicar en plantillas

En cada plantilla que muestra montos, al tope (después de `{% extends %}`):

```html
{% load finanzas_filters %}
```

Y reemplazar:

| Antes | Después |
|---|---|
| `{{ p.monto_bs }}` | `{{ p.monto_bs|bs }}` |
| `{{ p.monto_usd }}` | `{{ p.monto_usd|usd }}` |
| `{{ pago.monto_bs }}` | `{{ pago.monto_bs|bs }}` |
| `{{ pago.monto_usd }}` | `{{ pago.monto_usd|usd }}` |
| `{{ m.monto_usd }}` (sin `$`) | `{{ m.monto_usd|usd }}` |

**Plantillas a modificar:**
- `templates/finanzas/mis_pagos.html`
- `templates/finanzas/bandeja.html`
- `templates/finanzas/detalle.html`
- `templates/finanzas/reportar.html` (en bloque de mensualidades pendientes y total esperado)

### 9.4 Commit

```bash
git add finanzas/templatetags/ templates/finanzas/
git commit -m "feat(finanzas): filtros de plantilla para formato venezolano (Bs/USD)"
```

---

## 10. FASE 7 — QA

**Tiempo:** 30 min.

### 10.1 Tests manuales obligatorios

**Test del bug #1 (cobertura insuficiente):**

- [ ] Tener una mensualidad de $15 USD pendiente.
- [ ] Como representante, reportar pago de **900 Bs** vinculado a esa mensualidad.
- [ ] Como admin, abrir detalle. Verificar que muestra "Total esperado: $15.00".
- [ ] La tasa debe estar pre-cargada por DolarAPI (~486).
- [ ] Click "Aprobar".
- [ ] **Resultado esperado:** mensaje rojo — "Cobertura insuficiente. Pago = 1.85 USD, mensualidades = 15.00 USD. Faltan 13.15 USD".
- [ ] Verificar que la mensualidad sigue como pendiente.
- [ ] Verificar que el pago sigue como PENDIENTE.

**Test de cobertura exacta:**

- [ ] Reportar pago de **7290 Bs** (= 15 USD a tasa 486) vinculado a mensualidad de $15.
- [ ] Aprobar (tasa pre-cargada).
- [ ] **Resultado esperado:** se aprueba. Mensualidad marcada como pagada.

**Test de tolerancia:**

- [ ] Reportar pago de **7000 Bs** (= 14.40 USD a tasa 486) vinculado a $15.
- [ ] Diferencia: $0.60 (mayor a tolerancia).
- [ ] Aprobar → debe bloquearse.
- [ ] Reportar pago de **7050 Bs** (= 14.51 USD).
- [ ] Diferencia: $0.49 (dentro de tolerancia).
- [ ] Aprobar → debe pasar.

**Test del bug #2 (decimales en Telegram):**

- [ ] Aprobar cualquier pago.
- [ ] Verificar mensaje en Telegram con formato:
  ```
  ✅ Tu pago #N fue APROBADO.
  Monto: 7.290,00 Bs ($ 15,00)
  Concepto: ...
  ```
- [ ] NO deben aparecer 27 decimales.
- [ ] Coma decimal y punto de miles correctos.

**Test de rechazo:**

- [ ] Rechazar un pago.
- [ ] Verificar mensaje Telegram con `formato_bs` aplicado.

**Test de form de reporte:**

- [ ] Como representante, ir a `/finanzas/reportar/`.
- [ ] Seleccionar mensualidad de $15 → debe mostrar "Total seleccionado: $ 15,00".
- [ ] Seleccionar dos de $15 cada una → "$ 30,00".
- [ ] Deseleccionar → "$ 0,00".

**Test de filtros de plantilla:**

- [ ] Ir a "Mis Pagos" → verificar formato `1.250,00 Bs` y `$ 15,00`.
- [ ] Ir a bandeja admin → mismo formato.
- [ ] Detalle de pago → mismo formato en todos los campos de monto.

**Test sin mensualidades vinculadas:**

- [ ] Reportar pago sin seleccionar ninguna mensualidad.
- [ ] Aprobar con cualquier tasa.
- [ ] **Resultado esperado:** se aprueba sin validación de cobertura.

### 10.2 Commit final

```bash
git add -A
git commit -m "chore(finanzas): QA de mejoras v1.2"
```

---

## 11. Trampas conocidas

1. **El pago de Yannisito ya aprobado en producción está incorrecto.** Después de aplicar este parche, ir a Django admin → Mensualidades → marcar manualmente la de Yannisito como `pagada=False` para que vuelva a aparecer como deudor. El parche previene futuros errores pero no rehace historia.

2. **`label_from_instance` debe asignarse después de setear el queryset.** Si se asigna antes, no aplica.

3. **Los filtros de plantilla requieren `{% load %}` en cada template** que los use. No es global.

4. **El JavaScript del total esperado lee desde un objeto `montosMensualidad`** generado por Django. Si el queryset cambia (filtros, ordering), regenerar el mapa.

5. **`Decimal('0.50')` para la tolerancia, no `0.50` float.** Mezclar Decimal con float lanza `TypeError` o pierde precisión.

6. **`ROUND_HALF_UP` es el estándar contable**, no el default de Python (`ROUND_HALF_EVEN`, banker's rounding). Importante usar el primero para que los redondeos sean predecibles.

7. **El JS selecciona checkboxes con `.mensualidad-check:checked`.** Si Django renombra la clase del widget, ajustar.

8. **La tasa pre-cargada por DolarAPI (v1.3) funciona en simbiosis con la validación de cobertura.** Si DolarAPI falla y el admin ingresa tasa manual, la validación sigue funcionando igual — usa la tasa que esté en el form.

9. **El import circular potencial:** `views.py` importa de `telegram_bot.py` y `models.py` importa `TOLERANCIA_COBERTURA_USD`. Mantener el import de `notificar_pago_aprobado` y `notificar_pago_rechazado` dentro de las vistas (lazy import), no al tope del archivo.

---

## 12. Resumen del plan

| Fase | Tarea | Tiempo | Commit |
|---|---|---|---|
| **1** | Redondeo de monto_usd en `save()` | 15 min | `fix(finanzas): redondear monto_usd a 2 decimales con HALF_UP` |
| **2** | Validación de cobertura en `aprobar()` | 30 min | `fix(finanzas): bloquear aprobación si pago no cubre mensualidades vinculadas` |
| **3** | Helpers de formato + notificaciones Telegram | 30 min | `fix(finanzas): notificaciones Telegram con formato venezolano` |
| **4** | Total esperado en form de reporte | 30 min | `feat(finanzas): mostrar total USD esperado al seleccionar mensualidades` |
| **5** | Comparación cobertura en detalle admin | 20 min | `feat(finanzas): mostrar comparación cobertura en detalle de pago` |
| **6** | Filtros de plantilla Bs/USD | 20 min | `feat(finanzas): filtros de plantilla para formato venezolano (Bs/USD)` |
| **7** | QA | 30 min | `chore(finanzas): QA de mejoras v1.2` |
| **TOTAL** | | **~2h 55min** | |

---

## 13. Mensaje de PR sugerido

```
fix: corregir cobertura de mensualidades + formato de montos

## Bugs corregidos
- Pagos insuficientes ya no marcan mensualidades como pagadas (bug crítico financiero)
- Notificaciones Telegram ya no muestran 27 decimales en montos USD
- Aplicado formato venezolano (Bs / $ con coma decimal) en notificaciones y plantillas

## Cambios
- Validación de cobertura USD al aprobar pago, con tolerancia de $0.50
- Redondeo HALF_UP a 2 decimales en cálculo de monto_usd
- Filtros de plantilla `bs` y `usd` para formato consistente
- Total USD calculado en vivo al seleccionar mensualidades en el form
- Bloque de comparación cobertura visible en detalle admin
- Funciona en conjunto con la tasa pre-cargada de DolarAPI (v1.3)

```

---

**Fin del PRD.**

---

