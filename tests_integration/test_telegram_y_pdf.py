import pytest
from datetime import date
from decimal import Decimal
from django.urls import reverse
from finanzas.models import Pago
from core.models import CatBanco, CatEstadoPago, CatMetodoPago


@pytest.mark.integration
def test_notificar_pago_aprobado_envia_mensaje_con_formato_correcto(
    representante_con_user, comprobante_pdf, mock_telegram
):
    from finanzas.telegram_bot import notificar_pago_aprobado
    
    banco, _ = CatBanco.objects.get_or_create(codigo_sudeban='0134', defaults={'nombre': 'Banesco'})
    metodo, _ = CatMetodoPago.objects.get_or_create(codigo='PAGO_MOVIL', defaults={'nombre': 'Pago Móvil'})
    est_apr, _ = CatEstadoPago.objects.get_or_create(codigo='APROBADO', defaults={'descripcion': 'Aprobado'})

    pago = Pago.objects.create(
        representante=representante_con_user,
        concepto='Pago de Junio 2026',
        metodo=metodo,
        banco_emisor=banco,
        referencia='12345689',
        monto_bs=Decimal('500.00'),
        tasa_bcv=Decimal('50.0000'),
        fecha_pago='2026-06-08',
        comprobante=comprobante_pdf,
        estado=est_apr
    )
    pago.refresh_from_db()
    
    notificar_pago_aprobado(pago)
    
    assert len(mock_telegram) == 1
    texto = mock_telegram[0]['texto']
    assert f'#{pago.id}' in texto
    assert 'APROBADO' in texto
    assert 'Bs' in texto
    assert '$' in texto


@pytest.mark.integration
def test_notificar_pago_sin_chat_id_no_lanza_error(
    representante_con_user, comprobante_pdf, mock_telegram
):
    from finanzas.telegram_bot import notificar_pago_aprobado
    
    representante_con_user.telegram_chat_id = ''
    representante_con_user.save()
    
    banco, _ = CatBanco.objects.get_or_create(codigo_sudeban='0134', defaults={'nombre': 'Banesco'})
    metodo, _ = CatMetodoPago.objects.get_or_create(codigo='PAGO_MOVIL', defaults={'nombre': 'Pago Móvil'})
    est_apr, _ = CatEstadoPago.objects.get_or_create(codigo='APROBADO', defaults={'descripcion': 'Aprobado'})

    pago = Pago.objects.create(
        representante=representante_con_user,
        concepto='Pago de Junio 2026',
        metodo=metodo,
        banco_emisor=banco,
        referencia='12345690',
        monto_bs=Decimal('500.00'),
        tasa_bcv=Decimal('50.0000'),
        fecha_pago='2026-06-08',
        comprobante=comprobante_pdf,
        estado=est_apr
    )
    pago.refresh_from_db()
    
    success = notificar_pago_aprobado(pago)
    assert success is False
    assert len(mock_telegram) == 0


@pytest.mark.integration
def test_descargar_ficha_tecnica_pdf_retorna_content_type_pdf(
    client_representante, atleta_de
):
    url = reverse('atleta_ficha_pdf', args=[atleta_de.id])
    response = client_representante.get(url)
    assert response.status_code == 200
    assert response['Content-Type'] == 'application/pdf'


@pytest.mark.integration
def test_representante_no_puede_descargar_ficha_de_atleta_ajeno(
    client_representante, categoria
):
    from django.contrib.auth.models import User
    from filiacion.models import Representante, Atleta
    from core.models import CatPosicion, CatLateralidad
    
    otro_user = User.objects.create_user(username='otherrep5', password='ClaveSegura123!')
    otro_rep = Representante.objects.create(
        cedula_identidad='22222226', nombres='Otro', apellidos='Rep',
        telefono_principal='04141112233', direccion_habitacion='Caracas',
        correo_electronico='other5@test.com', usuario=otro_user
    )
    pos, _ = CatPosicion.objects.get_or_create(codigo='DEL', defaults={'nombre': 'Delantero'})
    lat, _ = CatLateralidad.objects.get_or_create(nombre='Derecho')

    atleta_ajeno = Atleta.objects.create(
        representante=otro_rep, categoria=categoria,
        nombres='Juan', apellidos='Gomez',
        fecha_nacimiento=date(2017, 5, 20),
        lateralidad=lat, posicion=pos
    )
    
    url = reverse('atleta_ficha_pdf', args=[atleta_ajeno.id])
    response = client_representante.get(url)
    assert response.status_code == 403
