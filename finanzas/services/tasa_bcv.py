# finanzas/services/tasa_bcv.py
"""
Servicio de integración con DolarAPI (https://ve.dolarapi.com).
Provee la tasa oficial BCV con cache local y tolerancia a fallos.
"""
import logging
from datetime import date, datetime
from decimal import Decimal
import requests
from django.utils import timezone
from finanzas.models import TasaBCV

logger = logging.getLogger(__name__)

API_BASE = 'https://ve.dolarapi.com/v1'
ENDPOINT_ACTUAL = f'{API_BASE}/dolares/oficial'
ENDPOINT_HISTORICO = f'{API_BASE}/historicos/dolares/oficial'
TIMEOUT_SEGUNDOS = 5


def obtener_tasa(fecha_objetivo=None):
    """
    Devuelve la tasa BCV para una fecha. Si no se especifica, hoy.

    Flujo:
    1. Buscar en cache local (TasaBCV).
    2. Si no existe, llamar DolarAPI.
    3. Guardar en cache.
    4. Devolver Decimal o None si falla todo.

    Args:
        fecha_objetivo: date. Si None, usa hoy en zona Caracas.

    Returns:
        Decimal con la tasa, o None si no se pudo obtener.
    """
    if fecha_objetivo is None:
        fecha_objetivo = timezone.localdate()

    # 1. Cache hit
    cache = TasaBCV.objects.filter(fecha=fecha_objetivo).first()
    if cache:
        logger.debug(f'TasaBCV cache HIT para {fecha_objetivo}: {cache.tasa}')
        return cache.tasa

    # 2. Cache miss → API
    es_hoy = fecha_objetivo == timezone.localdate()

    try:
        if es_hoy:
            tasa = _fetch_actual()
        else:
            tasa = _fetch_historico(fecha_objetivo)
    except Exception as e:
        logger.warning(f'DolarAPI falló para {fecha_objetivo}: {e}')
        return None

    if tasa is None:
        return None

    # 3. Guardar en cache (idempotente)
    TasaBCV.objects.update_or_create(
        fecha=fecha_objetivo,
        defaults={'tasa': tasa, 'fuente': 'dolarapi'}
    )
    logger.info(f'TasaBCV API HIT para {fecha_objetivo}: {tasa}')
    return tasa


def _fetch_actual():
    """Trae la tasa del día desde DolarAPI."""
    r = requests.get(ENDPOINT_ACTUAL, timeout=TIMEOUT_SEGUNDOS)
    r.raise_for_status()
    data = r.json()
    promedio = data.get('promedio')
    if promedio is None or promedio == 0:
        logger.warning(f'DolarAPI devolvió promedio inválido: {data}')
        return None
    return Decimal(str(promedio))


def _fetch_historico(fecha_objetivo):
    """
    Trae el histórico completo y busca la tasa del día solicitado.
    Si no hay tasa exacta para esa fecha, usa la del día anterior más cercano.
    """
    r = requests.get(ENDPOINT_HISTORICO, timeout=TIMEOUT_SEGUNDOS)
    r.raise_for_status()
    data = r.json()
    if not isinstance(data, list):
        return None

    # Filtrar entradas con fecha <= fecha_objetivo, ordenar descendente, tomar primera
    candidatas = []
    for entry in data:
        try:
            fecha_str = entry.get('fecha', '')
            fecha_entry = datetime.fromisoformat(fecha_str).date()
            promedio = entry.get('promedio')
            if promedio and fecha_entry <= fecha_objetivo:
                candidatas.append((fecha_entry, Decimal(str(promedio))))
        except (ValueError, TypeError):
            continue

    if not candidatas:
        return None

    # La más cercana hacia atrás
    candidatas.sort(key=lambda x: x[0], reverse=True)
    return candidatas[0][1]


def refrescar_tasa_actual():
    """
    Fuerza la actualización de la tasa de hoy ignorando cache.
    Útil para un management command diario o botón de admin.
    """
    fecha_hoy = timezone.localdate()
    try:
        tasa = _fetch_actual()
    except Exception as e:
        logger.error(f'No se pudo refrescar tasa: {e}')
        return None

    if tasa is None:
        return None

    TasaBCV.objects.update_or_create(
        fecha=fecha_hoy,
        defaults={'tasa': tasa, 'fuente': 'dolarapi'}
    )
    return tasa
