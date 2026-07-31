import pytest
from decimal import Decimal
from django.urls import reverse
from finanzas.models import Pago, PagoAuditLog, Mensualidad, CAT_EstadoPago, CAT_Banco, CAT_MetodoPago


@pytest.mark.integration
def test_representante_reporta_pago_y_se_crea_en_estado_pendiente(
    client_representante, mensualidad_pendiente, comprobante_pdf
):
    banco, _ = CAT_Banco.objects.get_or_create(codigo_sudeban='0134', defaults={'nombre': 'Banesco'})
    metodo, _ = CAT_MetodoPago.objects.get_or_create(codigo='PAGO_MOVIL', defaults={'nombre': 'Pago Móvil'})

    url = reverse('finanzas:reportar')
    data = {
        'metodo': metodo.id,
        'banco_emisor': banco.id,
        'referencia': '12345678',
        'monto_bs': '500.00',
        'fecha_pago': '2026-06-08',
        'comprobante': comprobante_pdf,
        'mensualidades': [mensualidad_pendiente.id],
    }
    response = client_representante.post(url, data)
    assert response.status_code == 302
    pago = Pago.objects.latest('id')
    assert pago.estado.codigo == 'PENDIENTE'
    assert pago.monto_bs == Decimal('500.00')


@pytest.mark.integration
def test_pago_creado_genera_audit_log_con_accion_creado(
    client_representante, mensualidad_pendiente, comprobante_pdf
):
    banco, _ = CAT_Banco.objects.get_or_create(codigo_sudeban='0134', defaults={'nombre': 'Banesco'})
    metodo, _ = CAT_MetodoPago.objects.get_or_create(codigo='PAGO_MOVIL', defaults={'nombre': 'Pago Móvil'})

    url = reverse('finanzas:reportar')
    data = {
        'metodo': metodo.id,
        'banco_emisor': banco.id,
        'referencia': '12345679',
        'monto_bs': '500.00',
        'fecha_pago': '2026-06-08',
        'comprobante': comprobante_pdf,
        'mensualidades': [mensualidad_pendiente.id],
    }
    client_representante.post(url, data)
    pago = Pago.objects.latest('id')
    audit = PagoAuditLog.objects.filter(pago=pago, accion='CREADO').first()
    assert audit is not None
    assert audit.estado_nuevo == 'PENDIENTE'


@pytest.mark.integration
def test_mensualidades_seleccionadas_quedan_vinculadas_al_pago_pero_no_pagadas(
    client_representante, mensualidad_pendiente, comprobante_pdf
):
    banco, _ = CAT_Banco.objects.get_or_create(codigo_sudeban='0134', defaults={'nombre': 'Banesco'})
    metodo, _ = CAT_MetodoPago.objects.get_or_create(codigo='PAGO_MOVIL', defaults={'nombre': 'Pago Móvil'})

    url = reverse('finanzas:reportar')
    data = {
        'metodo': metodo.id,
        'banco_emisor': banco.id,
        'referencia': '12345680',
        'monto_bs': '500.00',
        'fecha_pago': '2026-06-08',
        'comprobante': comprobante_pdf,
        'mensualidades': [mensualidad_pendiente.id],
    }
    client_representante.post(url, data)
    pago = Pago.objects.latest('id')
    mensualidad = Mensualidad.objects.get(id=mensualidad_pendiente.id)
    assert mensualidad.pago == pago
    assert mensualidad.esta_pagada is False


@pytest.mark.integration
def test_tesorero_aprueba_pago_marca_mensualidades_pagadas(
    client_tesorero, representante_con_user, mensualidad_pendiente, comprobante_pdf
):
    banco, _ = CAT_Banco.objects.get_or_create(codigo_sudeban='0134', defaults={'nombre': 'Banesco'})
    metodo, _ = CAT_MetodoPago.objects.get_or_create(codigo='PAGO_MOVIL', defaults={'nombre': 'Pago Móvil'})
    est_pen, _ = CAT_EstadoPago.objects.get_or_create(codigo='PENDIENTE', defaults={'descripcion': 'Pendiente'})

    pago = Pago.objects.create(
        representante=representante_con_user,
        concepto='Test',
        metodo=metodo,
        banco_emisor=banco,
        referencia='12345681',
        monto_bs=Decimal('500.00'),
        fecha_pago='2026-06-08',
        comprobante=comprobante_pdf,
        estado=est_pen
    )
    mensualidad_pendiente.pago = pago
    mensualidad_pendiente.save()

    url = reverse('finanzas:aprobar', args=[pago.id])
    response = client_tesorero.post(url, {'tasa_bcv': '50.0000'})
    assert response.status_code == 302
    
    pago.refresh_from_db()
    assert pago.estado.codigo == 'APROBADO'
    mensualidad_pendiente.refresh_from_db()
    assert mensualidad_pendiente.esta_pagada is True


@pytest.mark.integration
def test_aprobar_pago_con_cobertura_insuficiente_no_marca_mensualidades_pagadas(
    client_tesorero, representante_con_user, atleta_de, comprobante_pdf
):
    banco, _ = CAT_Banco.objects.get_or_create(codigo_sudeban='0134', defaults={'nombre': 'Banesco'})
    metodo, _ = CAT_MetodoPago.objects.get_or_create(codigo='PAGO_MOVIL', defaults={'nombre': 'Pago Móvil'})
    est_pen, _ = CAT_EstadoPago.objects.get_or_create(codigo='PENDIENTE', defaults={'descripcion': 'Pendiente'})

    mensualidad_cara = Mensualidad.objects.create(
        atleta=atleta_de,
        periodo_mes=6,
        periodo_anio=2026,
        monto_usd=Decimal('100.00'),
        fecha_vencimiento='2026-06-30'
    )
    pago = Pago.objects.create(
        representante=representante_con_user,
        concepto='Test',
        metodo=metodo,
        banco_emisor=banco,
        referencia='12345684',
        monto_bs=Decimal('100.00'),
        fecha_pago='2026-06-08',
        comprobante=comprobante_pdf,
        estado=est_pen
    )
    mensualidad_cara.pago = pago
    mensualidad_cara.save()

    url = reverse('finanzas:aprobar', args=[pago.id])
    response = client_tesorero.post(url, {'tasa_bcv': '50.0000'})
    assert response.status_code == 302
    pago.refresh_from_db()
    assert pago.estado.codigo == 'PENDIENTE'
    mensualidad_cara.refresh_from_db()
    assert mensualidad_cara.esta_pagada is False
