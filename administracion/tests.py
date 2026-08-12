from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

from administracion.models import (
    Personal, Categoria, CategoriaEntrenadores
)
from core.models import CatCargo, CatLicencia, CatGenero


def crear_usuario(username='admin01', password='ClaveSegura123!'):
    return User.objects.create_user(username=username, password=password)


def crear_cargo(nombre='General'):
    cargo, _ = CatCargo.objects.get_or_create(nombre=nombre)
    return cargo


def crear_licencia(nombre='Licencia FVF'):
    lic, _ = CatLicencia.objects.get_or_create(nombre=nombre)
    return lic


def crear_genero(nombre='Masculino'):
    gen, _ = CatGenero.objects.get_or_create(nombre=nombre)
    return gen


def crear_personal(usuario=None, cargo=None, cedula='V-11223344', nombres='María', apellidos='Coordina'):
    if cargo is None:
        cargo = crear_cargo()
    return Personal.objects.create(
        usuario=usuario,
        cargo=cargo,
        cedula_identidad=cedula,
        nombres=nombres,
        apellidos=apellidos,
        telefono='04141234567',
        activo=True,
    )


def crear_categoria(nombre='Sub-9', genero=None, anio_min=2017, anio_max=2018, supervisor=None, delegado=None):
    if genero is None:
        genero = crear_genero()
    if supervisor is None:
        supervisor = crear_personal(cedula='V-99999999')
    cat = Categoria(
        nombre=nombre,
        anio_nacimiento_min=anio_min,
        anio_nacimiento_max=anio_max,
        genero=genero,
        coordinador_supervisor=supervisor,
        delegado=delegado,
    )
    cat.full_clean()
    cat.save()
    return cat


class PersonalTestCase(TestCase):
    def test_personal_se_crea_correctamente(self):
        user = crear_usuario()
        personal = crear_personal(usuario=user)
        self.assertEqual(Personal.objects.count(), 1)
        self.assertEqual(user.perfil_personal, personal)

    def test_categoria_clean_valida_anios_nacimiento(self):
        cat = Categoria(
            nombre='Sub-Invalida',
            anio_nacimiento_min=2020,
            anio_nacimiento_max=2015,
            genero=crear_genero(),
            coordinador_supervisor=crear_personal(cedula='V-88888888')
        )
        with self.assertRaises(ValidationError):
            cat.full_clean()
