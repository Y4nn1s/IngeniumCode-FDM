from datetime import date
from decimal import Decimal
from django.test import TestCase
from django.utils import timezone

from filiacion.models import Representante, Atleta, CAT_Posicion, CAT_Lateralidad
from administracion.models import Categoria, Personal, CAT_Cargo, CAT_Genero
from deportivo.models import (
    Partido, Estadistica, EvaluacionTecnica, EvaluacionPsicosocial,
    CAT_TipoPartido, CAT_CondicionPartido
)


def crear_partido(rival="Rayo Zuliano", gf=2, gc=1):
    cargo, _ = CAT_Cargo.objects.get_or_create(nombre='Deportivo')
    gen, _ = CAT_Genero.objects.get_or_create(nombre='Masculino')
    pers, _ = Personal.objects.get_or_create(
        cedula_identidad='V-66666666',
        defaults={'cargo': cargo, 'nombres': 'Coord', 'apellidos': 'Sup', 'telefono': '04141112233'}
    )
    cat, _ = Categoria.objects.get_or_create(
        nombre='Sub-11',
        defaults={'anio_nacimiento_min': 2015, 'anio_nacimiento_max': 2016, 'genero': gen, 'coordinador_supervisor': pers}
    )
    
    tipo, _ = CAT_TipoPartido.objects.get_or_create(codigo='OFICIAL', defaults={'nombre': 'Oficial'})
    cond, _ = CAT_CondicionPartido.objects.get_or_create(codigo='CASA', defaults={'nombre': 'Casa'})
    
    return Partido.objects.create(
        categoria=cat,
        tipo=tipo,
        condicion=cond,
        fecha_hora=timezone.now(),
        equipo_rival=rival,
        goles_favor_escuela=gf,
        goles_contra_rival=gc,
        procesado=True
    )


class DeportivoTestCase(TestCase):
    def test_partido_calcula_resultado_dinamico(self):
        p_victoria = crear_partido(gf=3, gc=1)
        self.assertEqual(p_victoria.resultado, 'VICTORIA')

        p_empate = crear_partido(rival="Titanes", gf=2, gc=2)
        self.assertEqual(p_empate.resultado, 'EMPATE')

        p_derrota = crear_partido(rival="Zulia FC", gf=0, gc=2)
        self.assertEqual(p_derrota.resultado, 'DERROTA')
