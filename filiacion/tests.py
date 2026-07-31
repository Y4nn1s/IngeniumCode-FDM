from datetime import date
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

from filiacion.models import Representante, Atleta, CAT_Posicion, CAT_Lateralidad
from administracion.models import Categoria, Personal, CAT_Cargo, CAT_Genero

User = get_user_model()


def crear_representante(cedula='12345678', correo='rep@test.com', usuario=None):
    return Representante.objects.create(
        cedula_identidad=cedula,
        nombres='Juan',
        apellidos='Pérez',
        telefono_principal='04141234567',
        direccion_habitacion='Calle de prueba',
        correo_electronico=correo,
        usuario=usuario,
    )


def crear_categoria(nombre='Sub-9'):
    cargo, _ = CAT_Cargo.objects.get_or_create(nombre='Deportivo')
    gen, _ = CAT_Genero.objects.get_or_create(nombre='Masculino')
    pers = Personal.objects.create(
        cargo=cargo, cedula_identidad='V-77777777', nombres='Coord', apellidos='Sup', telefono='04141112233'
    )
    return Categoria.objects.create(
        nombre=nombre,
        anio_nacimiento_min=2017,
        anio_nacimiento_max=2018,
        genero=gen,
        coordinador_supervisor=pers,
    )


def crear_atleta(representante=None, categoria=None, fecha_nacimiento=None,
                  cedula_identidad=None, numero_acta="ACTA-123"):
    if representante is None:
        representante = crear_representante()
    if categoria is None:
        categoria = crear_categoria()
    pos, _ = CAT_Posicion.objects.get_or_create(codigo='DEL', defaults={'nombre': 'Delantero'})
    lat, _ = CAT_Lateralidad.objects.get_or_create(nombre='Derecho')
    
    atl = Atleta(
        representante=representante,
        categoria=categoria,
        numero_acta_nacimiento=numero_acta,
        cedula_identidad=cedula_identidad,
        nombres='Pedro',
        apellidos='Pérez',
        fecha_nacimiento=fecha_nacimiento or date(2018, 3, 15), # 8 años aprox
        peso_kg=25.0,
        altura_mts=1.20,
        posicion=pos,
        lateralidad=lat,
    )
    atl.full_clean()
    atl.save()
    return atl


class FiliacionTestCase(TestCase):
    def test_representante_se_crea_correctamente(self):
        rep = crear_representante()
        self.assertEqual(Representante.objects.count(), 1)
        self.assertEqual(rep.cedula_identidad, '12345678')

    def test_atleta_requiere_cedula_si_edad_mayor_igual_9(self):
        rep = crear_representante()
        cat = crear_categoria()
        pos, _ = CAT_Posicion.objects.get_or_create(codigo='DEF', defaults={'nombre': 'Defensa'})
        lat, _ = CAT_Lateralidad.objects.get_or_create(nombre='Izquierdo')

        # Atleta de 10 años sin cédula
        atl = Atleta(
            representante=rep,
            categoria=cat,
            nombres='Carlos',
            apellidos='Gómez',
            fecha_nacimiento=date(2016, 1, 1),
            posicion=pos,
            lateralidad=lat,
            cedula_identidad=None
        )
        with self.assertRaises(ValidationError):
            atl.full_clean()
