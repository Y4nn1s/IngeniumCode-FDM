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
