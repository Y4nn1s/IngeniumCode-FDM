# core/tests.py
# Pruebas unitarias — Módulo Core
# PRD v1.0 | IngeniumCode-FDM | 8 de junio de 2026

from django.core.exceptions import ValidationError
from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse, NoReverseMatch

from core.models import CatCargo
from core.validators import (
    validar_cedula_venezolana,
    normalizar_cedula,
    CEDULA_REGEX,
)
from administracion.models import Personal


# ═══════════════════════════════════════════════════════════════
# Helpers de fábrica
# ═══════════════════════════════════════════════════════════════

def crear_usuario_test(username='testuser', password='ClaveSegura123!'):
    """Crea un User para tests de vista con login."""
    return User.objects.create_user(username=username, password=password)


# ═══════════════════════════════════════════════════════════════
# FASE 5 — Vista dashboard de core
# ═══════════════════════════════════════════════════════════════

class Fase5_DashboardCoreTestCase(TestCase):
    """Valida el control de acceso y renderizado del dashboard."""

    def setUp(self):
        self.client = Client()
        self.user = crear_usuario_test()

    def test_dashboard_sin_login_redirige(self):
        """Un usuario anónimo debe ser redirigido al login al acceder al dashboard."""
        try:
            url = reverse('dashboard')
        except NoReverseMatch:
            url = '/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)

    def test_dashboard_con_login_permite_acceso(self):
        """Un usuario autenticado debe poder acceder al dashboard."""
        self.client.login(username='testuser', password='ClaveSegura123!')
        try:
            url = reverse('dashboard')
        except NoReverseMatch:
            url = '/'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_dashboard_usa_template_correcto(self):
        """El dashboard debe renderizar el template 'core/dashboard.html'."""
        self.client.login(username='testuser', password='ClaveSegura123!')
        try:
            url = reverse('dashboard')
        except NoReverseMatch:
            url = '/'
        response = self.client.get(url)
        templates_usados = [t.name for t in response.templates if t.name]
        self.assertIn('core/dashboard.html', templates_usados)


# ═══════════════════════════════════════════════════════════════
# Validador compartido de cédula venezolana (core.validators)
# ═══════════════════════════════════════════════════════════════

class ValidadorCedulaVenezolanaTestCase(TestCase):
    """La cédula es numérica, entre 1 y 8 dígitos (norma venezolana)."""

    def test_cedula_de_8_digitos_pasa(self):
        validar_cedula_venezolana('12345678')

    def test_cedula_corta_pasa(self):
        """Cédulas históricas de menos de 8 dígitos son válidas."""
        validar_cedula_venezolana('12345')

    def test_cedula_de_1_digito_pasa(self):
        validar_cedula_venezolana('1')

    def test_cedula_de_9_digitos_es_rechazada(self):
        with self.assertRaises(ValidationError):
            validar_cedula_venezolana('123456789')

    def test_cedula_con_letras_es_rechazada(self):
        with self.assertRaises(ValidationError):
            validar_cedula_venezolana('V1234567')

    def test_cedula_con_espacios_es_rechazada(self):
        with self.assertRaises(ValidationError):
            validar_cedula_venezolana('1234 5678')

    def test_cedula_vacia_es_rechazada(self):
        with self.assertRaises(ValidationError):
            validar_cedula_venezolana('')

    def test_regex_acepta_solo_digitos(self):
        self.assertTrue(CEDULA_REGEX.match('87654321'))
        self.assertIsNone(CEDULA_REGEX.match('V-87654321'))


class NormalizarCedulaTestCase(TestCase):
    """La normalización descarta prefijos V-/E- y espacios antes de almacenar."""

    def test_prefijo_v_mayuscula(self):
        self.assertEqual(normalizar_cedula('V-12345678'), '12345678')

    def test_prefijo_e_minuscula(self):
        self.assertEqual(normalizar_cedula('e-8765432'), '8765432')

    def test_prefijo_sin_guion(self):
        self.assertEqual(normalizar_cedula('V1234567'), '1234567')

    def test_solo_espacios_externos(self):
        self.assertEqual(normalizar_cedula('  12345678  '), '12345678')

    def test_ya_normalizada_se_mantiene(self):
        self.assertEqual(normalizar_cedula('12345678'), '12345678')

    def test_valor_invalido_pasa_tal_cual_para_que_el_validador_lo_rechace(self):
        self.assertEqual(normalizar_cedula('12-34.567'), '12-34.567')

    def test_none_se_mantiene(self):
        self.assertIsNone(normalizar_cedula(None))


class ValidadorCedulaEnModelosTestCase(TestCase):
    """Los modelos con cédula tienen el validador adjunto (corre en full_clean)."""

    def test_personal_rechaza_cedula_con_prefijo_en_full_clean(self):
        personal = Personal(
            cargo=CatCargo.objects.create(nombre='Entrenador'),
            cedula_identidad='V-12345678',
            nombres='Juan',
            apellidos='Pérez',
            telefono='04141234567',
        )
        with self.assertRaises(ValidationError) as ctx:
            personal.full_clean()
        self.assertIn('cedula_identidad', ctx.exception.message_dict)

    def test_personal_acepta_cedula_de_8_digitos(self):
        personal = Personal(
            cargo=CatCargo.objects.create(nombre='Delegado'),
            cedula_identidad='12345678',
            nombres='Juan',
            apellidos='Pérez',
            telefono='04141234567',
        )
        try:
            personal.full_clean()
        except ValidationError as exc:
            self.assertNotIn('cedula_identidad', exc.message_dict)
