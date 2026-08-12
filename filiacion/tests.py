from datetime import date
from decimal import Decimal
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.db import IntegrityError, transaction

from filiacion.models import Representante, Atleta
from administracion.models import Categoria, Personal
from core.models import CatCargo, CatGenero, CatPosicion, CatLateralidad

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
    cargo, _ = CatCargo.objects.get_or_create(nombre='Deportivo')
    gen, _ = CatGenero.objects.get_or_create(nombre='Masculino')
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
    pos, _ = CatPosicion.objects.get_or_create(codigo='DEL', defaults={'nombre': 'Delantero'})
    lat, _ = CatLateralidad.objects.get_or_create(nombre='Derecho')
    
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
        pos, _ = CatPosicion.objects.get_or_create(codigo='DEF', defaults={'nombre': 'Defensa'})
        lat, _ = CatLateralidad.objects.get_or_create(nombre='Izquierdo')

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

    def _atleta_base(self, **kwargs):
        rep = crear_representante()
        cat = crear_categoria()
        pos, _ = CatPosicion.objects.get_or_create(codigo='DEF', defaults={'nombre': 'Defensa'})
        lat, _ = CatLateralidad.objects.get_or_create(nombre='Izquierdo')
        datos = {
            'representante': rep,
            'categoria': cat,
            'nombres': 'Luis',
            'apellidos': 'Rodríguez',
            'fecha_nacimiento': date(2018, 1, 1),
            'numero_acta_nacimiento': 'ACTA-TEST',
            'posicion': pos,
            'lateralidad': lat,
        }
        datos.update(kwargs)
        return Atleta(**datos)

    def test_atleta_fecha_nacimiento_incoherente_con_categoria(self):
        # Sub-9: años 2017-2018 → nacido en 2016 no aplica
        atl = self._atleta_base(
            fecha_nacimiento=date(2016, 6, 1),
            cedula_identidad='12345679'
        )
        with self.assertRaises(ValidationError) as ctx:
            atl.full_clean()
        self.assertIn('categoria', ctx.exception.message_dict)

    def test_atleta_peso_anomalo_para_edad_rechazado(self):
        # 8 años → banda Sub-9: máx. 45 kg
        atl = self._atleta_base(peso_kg=Decimal('50.00'), altura_mts=Decimal('1.20'))
        with self.assertRaises(ValidationError) as ctx:
            atl.full_clean()
        self.assertIn('peso_kg', ctx.exception.message_dict)

    def test_atleta_peso_por_debajo_del_minimo_rechazado(self):
        atl = self._atleta_base(peso_kg=Decimal('8.00'), altura_mts=Decimal('1.20'))
        with self.assertRaises(ValidationError) as ctx:
            atl.full_clean()
        self.assertIn('peso_kg', ctx.exception.message_dict)

    def test_atleta_altura_anomala_para_edad_rechazada(self):
        # 8 años → máx. 1.60 mts
        atl = self._atleta_base(peso_kg=Decimal('30.00'), altura_mts=Decimal('1.70'))
        with self.assertRaises(ValidationError) as ctx:
            atl.full_clean()
        self.assertIn('altura_mts', ctx.exception.message_dict)

    def test_atleta_condicion_especial_omite_validacion_biometrica(self):
        atl = self._atleta_base(
            peso_kg=Decimal('60.00'),
            altura_mts=Decimal('1.80'),
            es_condicion_especial=True,
            observacion_medica='Sobrepeso diagnosticado por especialista.',
        )
        atl.full_clean()  # No debe lanzar ValidationError

    def test_atleta_condicion_especial_requiere_observacion_medica(self):
        atl = self._atleta_base(
            peso_kg=Decimal('60.00'),
            es_condicion_especial=True,
            observacion_medica='',
        )
        with self.assertRaises(ValidationError) as ctx:
            atl.full_clean()
        self.assertIn('observacion_medica', ctx.exception.message_dict)
