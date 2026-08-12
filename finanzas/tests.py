from datetime import date
from decimal import Decimal
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile

from filiacion.models import Representante, Atleta
from finanzas.models import (
    Pago, Mensualidad, TasaBCV, Patrocinante, Aporte
)
from core.models import (
    CatBanco, CatEstadoPago, CatMetodoPago, CatTipoPatrocinante, CatFuenteTasaBCV
)


def crear_representante(cedula='12345678', correo='rep@test.com'):
    return Representante.objects.create(
        cedula_identidad=cedula,
        nombres='Juan',
        apellidos='Pérez',
        telefono_principal='04141234567',
        direccion_habitacion='Calle de prueba',
        correo_electronico=correo,
    )


class FinanzasTestCase(TestCase):
    def setUp(self):
        self.rep = crear_representante()
        self.banco, _ = CatBanco.objects.get_or_create(codigo_sudeban='0102', defaults={'nombre': 'Banco de Venezuela'})
        self.metodo, _ = CatMetodoPago.objects.get_or_create(codigo='PAGO_MOVIL', defaults={'nombre': 'Pago Móvil'})
        self.est_pen, _ = CatEstadoPago.objects.get_or_create(codigo='PENDIENTE', defaults={'descripcion': 'Pendiente'})
        self.est_apr, _ = CatEstadoPago.objects.get_or_create(codigo='APROBADO', defaults={'descripcion': 'Aprobado'})

    def test_pago_clean_valida_monto_bs_positivo(self):
        comp = SimpleUploadedFile("comprobante.png", b"file_content", content_type="image/png")
        pago = Pago(
            representante=self.rep,
            concepto="Pago Test",
            metodo=self.metodo,
            banco_emisor=self.banco,
            referencia="12345678",
            monto_bs=Decimal('0.00'),
            fecha_pago=date.today(),
            comprobante=comp,
            estado=self.est_pen
        )
        with self.assertRaises(ValidationError):
            pago.full_clean()

    def test_mensualidad_propiedad_esta_pagada(self):
        atl = Atleta.objects.create(
            representante=self.rep,
            nombres='Pedrito',
            apellidos='Pérez',
            fecha_nacimiento=date(2018, 1, 1),
            peso_kg=20.0,
            altura_mts=1.10
        )
        mens = Mensualidad.objects.create(
            atleta=atl,
            periodo_mes=5,
            periodo_anio=2026,
            monto_usd=Decimal('15.00'),
            fecha_vencimiento=date(2026, 5, 10)
        )
        self.assertFalse(mens.esta_pagada)

        comp = SimpleUploadedFile("comp.png", b"file_content", content_type="image/png")
        pago = Pago.objects.create(
            representante=self.rep,
            concepto="Pago Aprobado",
            metodo=self.metodo,
            banco_emisor=self.banco,
            referencia="87654321",
            monto_bs=Decimal('547.50'),
            tasa_bcv=Decimal('36.50'),
            fecha_pago=date.today(),
            comprobante=comp,
            estado=self.est_apr
        )
        mens.pago = pago
        mens.save()

        self.assertTrue(mens.esta_pagada)

    def test_tasabcv_fuente_es_fk_a_catalogo(self):
        fuente, _ = CatFuenteTasaBCV.objects.get_or_create(
            codigo='DOLARAPI', defaults={'nombre': 'DolarAPI'}
        )
        tasa = TasaBCV.objects.create(
            fecha=date(2026, 8, 1),
            tasa=Decimal('36.5000'),
            fuente=fuente,
        )
        self.assertEqual(tasa.fuente.codigo, 'DOLARAPI')
        self.assertIn(fuente.codigo, str(tasa))

    def test_patrocinante_y_aporte_tipo_son_fk_a_catalogo(self):
        tipo, _ = CatTipoPatrocinante.objects.get_or_create(
            codigo='EMPRESA', defaults={'nombre': 'Empresa'}
        )
        pat = Patrocinante.objects.create(
            nombre_empresa='ACME Corp',
            tipo_ente=tipo,
            persona_contacto='Ana López',
        )
        apo = Aporte.objects.create(
            patrocinante=pat,
            fecha_aporte=date(2026, 8, 1),
            tipo=tipo,
            descripcion='Donación uniformes',
            valor_estimado_usd=Decimal('100.00'),
        )
        self.assertEqual(pat.tipo_ente.codigo, 'EMPRESA')
        self.assertEqual(apo.tipo.codigo, 'EMPRESA')
