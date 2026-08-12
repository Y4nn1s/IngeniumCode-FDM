import pytest
from datetime import date, timedelta
from decimal import Decimal
from django.contrib.auth.models import User, Group
from django.core.files.uploadedfile import SimpleUploadedFile
from django.utils import timezone

from filiacion.models import Representante, Atleta
from administracion.models import Categoria, Personal
from finanzas.models import Mensualidad, Pago
from core.models import CatPosicion, CatLateralidad, CatCargo, CatGenero


@pytest.fixture
def mock_telegram(monkeypatch):
    enviadas = []
    def fake_enviar_mensaje(chat_id, texto):
        enviadas.append({'chat_id': chat_id, 'texto': texto})
        return True
    monkeypatch.setattr('finanzas.telegram_bot.enviar_mensaje', fake_enviar_mensaje)
    return enviadas


@pytest.fixture(autouse=True)
def mock_tasa_bcv(monkeypatch):
    monkeypatch.setattr('finanzas.services.tasa_bcv.obtener_tasa', lambda fecha=None: Decimal('50.0000'))


@pytest.fixture
def representante_con_user(db):
    user = User.objects.create_user(
        username='12345678',
        password='ClaveSegura123!',
        email='rep@test.com'
    )
    rep = Representante.objects.create(
        cedula_identidad='12345678',
        nombres='Juan', apellidos='Pérez',
        telefono_principal='04141234567',
        direccion_habitacion='Calle de prueba',
        correo_electronico='rep@test.com',
        telegram_chat_id='999999',
        usuario=user,
    )
    user.refresh_from_db()
    return rep


@pytest.fixture
def tesorero(db):
    user = User.objects.create_user(username='tesorero01', password='ClaveSegura123!', is_staff=True)
    grupo, _ = Group.objects.get_or_create(name='Tesoreria')
    user.groups.add(grupo)
    return user


@pytest.fixture
def coord_general(db):
    user = User.objects.create_user(username='coord01', password='ClaveSegura123!', is_staff=True)
    grupo, _ = Group.objects.get_or_create(name='CoordinadorGeneral')
    user.groups.add(grupo)
    return user


@pytest.fixture
def entrenador_user(db):
    user = User.objects.create_user(username='entr01', password='ClaveSegura123!', is_staff=True)
    grupo, _ = Group.objects.get_or_create(name='Entrenador')
    user.groups.add(grupo)
    return user


@pytest.fixture
def categoria(db):
    cargo, _ = CatCargo.objects.get_or_create(nombre='Deportivo')
    gen, _ = CatGenero.objects.get_or_create(nombre='Masculino')
    pers = Personal.objects.create(cargo=cargo, cedula_identidad='V-55555555', nombres='Coord', apellidos='Sup', telefono='04141112233')
    return Categoria.objects.create(
        nombre='Sub-9',
        anio_nacimiento_min=2017,
        anio_nacimiento_max=2018,
        genero=gen,
        coordinador_supervisor=pers,
    )


@pytest.fixture
def atleta_de(representante_con_user, categoria):
    pos, _ = CatPosicion.objects.get_or_create(codigo='DEL', defaults={'nombre': 'Delantero'})
    lat, _ = CatLateralidad.objects.get_or_create(nombre='Derecho')
    return Atleta.objects.create(
        representante=representante_con_user,
        categoria=categoria,
        nombres='Pedro', apellidos='Pérez',
        fecha_nacimiento=date(2017, 3, 15),
        lateralidad=lat, posicion=pos,
    )


@pytest.fixture
def mensualidad_pendiente(atleta_de):
    return Mensualidad.objects.create(
        atleta=atleta_de,
        periodo_mes=6,
        periodo_anio=2026,
        monto_usd=Decimal('10.00'),
        fecha_vencimiento=timezone.now().date() + timedelta(days=15),
    )


@pytest.fixture
def comprobante_pdf():
    return SimpleUploadedFile('comprobante.pdf', b'contenido_pdf_mock', content_type='application/pdf')


@pytest.fixture
def client_representante(client, representante_con_user):
    client.login(username='12345678', password='ClaveSegura123!')
    return client


@pytest.fixture
def client_tesorero(client, tesorero):
    client.login(username='tesorero01', password='ClaveSegura123!')
    return client


@pytest.fixture
def client_coord_general(client, coord_general):
    client.login(username='coord01', password='ClaveSegura123!')
    return client


@pytest.fixture
def client_entrenador(client, entrenador_user):
    client.login(username='entr01', password='ClaveSegura123!')
    return client
