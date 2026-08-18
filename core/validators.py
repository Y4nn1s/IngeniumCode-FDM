"""Validadores compartidos de identificación venezolana.

La Cédula de Identidad venezolana es estrictamente numérica y su parte
significativa tiene entre 1 y 8 dígitos (la "cédula escolar" usaba otro
formato y fue eliminada del sistema). El sistema almacena SOLO los dígitos,
sin el prefijo de nacionalidad (V-/E-).
"""
import re

from django.core.exceptions import ValidationError

# Valor final almacenado: solo dígitos, 1 a 8.
CEDULA_REGEX = re.compile(r'^\d{1,8}$')

# Entrada aceptada en la UI: permite prefijo V-/E- (en mayúscula o minúscula)
# y espacios, que se descartan al normalizar.
_CEDULA_ENTRADA_REGEX = re.compile(r'^[VE]?-?\s*(\d{1,8})\s*$', re.IGNORECASE)


def validar_cedula_venezolana(value):
    """La cédula debe contener solo dígitos (máximo 8). Ej: 12345678."""
    if not CEDULA_REGEX.match(value or ''):
        raise ValidationError(
            'La cédula debe contener solo dígitos (máximo 8), sin letras ni '
            'prefijos V-/E-. Ej: 12345678'
        )


def normalizar_cedula(valor):
    """Quita espacios y el prefijo V-/E-; devuelve solo los dígitos.

    Si el valor no sigue el formato esperado se devuelve tal cual (recortado
    de espacios) para que el validador lo rechace con el mensaje correcto.
    """
    if valor is None:
        return valor
    entrada = valor.strip()
    match = _CEDULA_ENTRADA_REGEX.match(entrada)
    if match:
        return match.group(1)
    return entrada
