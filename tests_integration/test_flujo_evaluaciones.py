import pytest
from datetime import date
from django.urls import reverse
from deportivo.models import EvaluacionTecnica, EvaluacionPsicosocial
from administracion.models import Personal, CAT_Cargo, CAT_Licencia


@pytest.mark.integration
def test_entrenador_puede_crear_evaluacion_tecnica(
    client_entrenador, atleta_de
):
    cargo_ent, _ = CAT_Cargo.objects.get_or_create(nombre='Entrenador')
    lic_fvf, _ = CAT_Licencia.objects.get_or_create(nombre='Licencia FVF')
    ent = Personal.objects.create(
        cargo=cargo_ent, licencia=lic_fvf, cedula_identidad='V-99001122',
        nombres='Carlos', apellidos='Entrena', telefono='04141234567'
    )
    url = reverse('evaluacion_tecnica_create')
    data = {
        'atleta': atleta_de.id,
        'entrenador': ent.id,
        'fecha_evaluacion': '2026-06-08',
        'control_balon': '7.0',
        'conduccion': '8.0',
        'pase_corto': '8.0',
        'tiro': '9.0',
        'inteligencia_tactica': '10.0',
        'observaciones': 'Buen desempeño.'
    }
    response = client_entrenador.post(url, data)
    assert response.status_code == 302
    assert EvaluacionTecnica.objects.count() == 1


@pytest.mark.integration
def test_evaluacion_tecnica_vincula_correctamente_atleta_y_entrenador(
    client_entrenador, atleta_de
):
    cargo_ent, _ = CAT_Cargo.objects.get_or_create(nombre='Entrenador')
    lic_fvf, _ = CAT_Licencia.objects.get_or_create(nombre='Licencia FVF')
    ent = Personal.objects.create(
        cargo=cargo_ent, licencia=lic_fvf, cedula_identidad='V-99001123',
        nombres='Carlos', apellidos='Entrena', telefono='04141234567'
    )
    url = reverse('evaluacion_tecnica_create')
    data = {
        'atleta': atleta_de.id,
        'entrenador': ent.id,
        'fecha_evaluacion': '2026-06-08',
        'control_balon': '5.0',
        'conduccion': '5.0',
        'pase_corto': '5.0',
        'tiro': '5.0',
        'inteligencia_tactica': '5.0',
        'observaciones': ''
    }
    client_entrenador.post(url, data)
    eval_t = EvaluacionTecnica.objects.latest('id')
    assert eval_t.atleta == atleta_de
    assert eval_t.entrenador == ent


@pytest.mark.integration
def test_coord_deportivo_puede_crear_evaluacion_psicosocial(
    client_coord_general, coord_general, atleta_de
):
    cargo_dep, _ = CAT_Cargo.objects.get_or_create(nombre='Deportivo')
    coord_profile = Personal.objects.create(
        usuario=coord_general,
        cargo=cargo_dep,
        cedula_identidad='V-99001124',
        nombres='Maria', apellidos='Coordina', telefono='04141112233'
    )
    url = reverse('evaluacion_psicosocial_create')
    data = {
        'atleta': atleta_de.id,
        'evaluador': coord_profile.id,
        'fecha_evaluacion': '2026-06-08',
        'compromiso': '7.0',
        'puntualidad': '8.0',
        'companerismo': '9.0',
        'respeto': '10.0',
        'manejo_frustracion': '6.0',
        'observaciones_conductuales': 'Muy receptivo.'
    }
    response = client_coord_general.post(url, data)
    assert response.status_code == 302
    assert EvaluacionPsicosocial.objects.count() == 1


@pytest.mark.integration
def test_representante_no_puede_crear_evaluaciones(
    client_representante, atleta_de
):
    url = reverse('evaluacion_tecnica_create')
    response = client_representante.post(url, {})
    assert response.status_code == 403
