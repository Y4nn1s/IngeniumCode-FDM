import pytest
from decimal import Decimal
from django.urls import reverse
from finanzas.models import Pago, PagoAuditLog, Mensualidad
from core.models import CatBanco, CatEstadoPago, CatMetodoPago


@pytest.mark.integration
def test_tesorero_rechaza_pago_cambia_estado_a_rechazado(
    client_tesorero, representante_con_user, mensualidad_pendiente, comprobante_pdf
):
    banco, _ = CatBanco.objects.get_or_create(codigo_sudeban='0134', defaults={'nombre': 'Banesco'})
    metodo, _ = CatMetodoPago.objects.get_or_create(codigo='PAGO_MOVIL', defaults={'nombre': 'Pago Móvil'})
    est_pen, _ = CatEstadoPago.objects.get_or_create(codigo='PENDIENTE', defaults={'descripcion': 'Pendiente'})

    pago = Pago.objects.create(
        representante=representante_con_user,
        concepto='Test',
        metodo=metodo,
        banco_emisor=banco,
        referencia='12345685',
        monto_bs=Decimal('500.00'),
        fecha_pago='2026-06-08',
        comprobante=comprobante_pdf,
        estado=est_pen
    )
    mensualidad_pendiente.pago = pago
    mensualidad_pendiente.save()

    url = reverse('finanzas:rechazar', args=[pago.id])
    response = client_tesorero.post(url, {'motivo': 'Comprobante borroso.'})
    assert response.status_code == 302
    pago.refresh_from_db()
    assert pago.estado.codigo == 'RECHAZADO'


@pytest.mark.integration
def test_rechazar_pago_desvincula_mensualidades(
    client_tesorero, representante_con_user, mensualidad_pendiente, comprobante_pdf
):
    banco, _ = CatBanco.objects.get_or_create(codigo_sudeban='0134', defaults={'nombre': 'Banesco'})
    metodo, _ = CatMetodoPago.objects.get_or_create(codigo='PAGO_MOVIL', defaults={'nombre': 'Pago Móvil'})
    est_pen, _ = CatEstadoPago.objects.get_or_create(codigo='PENDIENTE', defaults={'descripcion': 'Pendiente'})

    pago = Pago.objects.create(
        representante=representante_con_user,
        concepto='Test',
        metodo=metodo,
        banco_emisor=banco,
        referencia='12345686',
        monto_bs=Decimal('500.00'),
        fecha_pago='2026-06-08',
        comprobante=comprobante_pdf,
        estado=est_pen
    )
    mensualidad_pendiente.pago = pago
    mensualidad_pendiente.save()

    url = reverse('finanzas:rechazar', args=[pago.id])
    client_tesorero.post(url, {'motivo': 'Comprobante borroso.'})
    
    mensualidad_pendiente.refresh_from_db()
    assert mensualidad_pendiente.pago is None
    assert mensualidad_pendiente.esta_pagada is False


@pytest.mark.integration
def test_rechazar_pago_guarda_motivo_y_genera_audit_log(
    client_tesorero, representante_con_user, mensualidad_pendiente, comprobante_pdf
):
    banco, _ = CatBanco.objects.get_or_create(codigo_sudeban='0134', defaults={'nombre': 'Banesco'})
    metodo, _ = CatMetodoPago.objects.get_or_create(codigo='PAGO_MOVIL', defaults={'nombre': 'Pago Móvil'})
    est_pen, _ = CatEstadoPago.objects.get_or_create(codigo='PENDIENTE', defaults={'descripcion': 'Pendiente'})

    pago = Pago.objects.create(
        representante=representante_con_user,
        concepto='Test',
        metodo=metodo,
        banco_emisor=banco,
        referencia='12345687',
        monto_bs=Decimal('500.00'),
        fecha_pago='2026-06-08',
        comprobante=comprobante_pdf,
        estado=est_pen
    )
    mensualidad_pendiente.pago = pago
    mensualidad_pendiente.save()

    url = reverse('finanzas:rechazar', args=[pago.id])
    client_tesorero.post(url, {'motivo': 'Comprobante borroso.'})
    
    pago.refresh_from_db()
    assert pago.motivo_rechazo == 'Comprobante borroso.'
    
    audit = PagoAuditLog.objects.filter(pago=pago, accion='RECHAZADO').first()
    assert audit is not None
    assert audit.detalles['motivo'] == 'Comprobante borroso.'


@pytest.mark.integration
def test_rechazar_pago_dispara_notificacion_telegram_de_rechazo(
    client_tesorero, representante_con_user, mensualidad_pendiente, comprobante_pdf, mock_telegram
):
    banco, _ = CatBanco.objects.get_or_create(codigo_sudeban='0134', defaults={'nombre': 'Banesco'})
    metodo, _ = CatMetodoPago.objects.get_or_create(codigo='PAGO_MOVIL', defaults={'nombre': 'Pago Móvil'})
    est_pen, _ = CatEstadoPago.objects.get_or_create(codigo='PENDIENTE', defaults={'descripcion': 'Pendiente'})

    pago = Pago.objects.create(
        representante=representante_con_user,
        concepto='Test',
        metodo=metodo,
        banco_emisor=banco,
        referencia='12345688',
        monto_bs=Decimal('500.00'),
        fecha_pago='2026-06-08',
        comprobante=comprobante_pdf,
        estado=est_pen
    )
    mensualidad_pendiente.pago = pago
    mensualidad_pendiente.save()

    url = reverse('finanzas:rechazar', args=[pago.id])
    client_tesorero.post(url, {'motivo': 'Comprobante borroso.'})
    
    assert len(mock_telegram) == 1
    assert 'RECHAZADO' in mock_telegram[0]['texto']
