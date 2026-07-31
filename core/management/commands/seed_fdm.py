# core/management/commands/seed_fdm.py
"""
Comando de gestión: seed_fdm
Crea datos de prueba venezolanos realistas para la plataforma FDM.
"""

import io
import random
import datetime
from decimal import Decimal

from django.conf import settings
from django.contrib.auth.models import User, Group
from django.core.files.base import ContentFile
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.utils import timezone

from PIL import Image

from administracion.models import (
    CAT_Cargo, CAT_Licencia, CAT_Genero,
    Personal, Categoria, CategoriaEntrenadores
)
from deportivo.models import (
    CAT_TipoPartido, CAT_CondicionPartido,
    Partido, Estadistica, EvaluacionTecnica, EvaluacionPsicosocial
)
from filiacion.models import (
    CAT_Posicion, CAT_Lateralidad,
    Representante, Atleta
)
from finanzas.models import (
    CAT_Banco, CAT_EstadoPago, CAT_MetodoPago,
    TasaBCV, Mensualidad, Pago, PagoAuditLog
)


# ─────────────────────────────────────────────
# Datos venezolanos hardcodeados (NO Faker)
# ─────────────────────────────────────────────

NOMBRES_MASC = [
    'José', 'Carlos', 'Luis', 'Pedro', 'Andrés', 'Diego', 'Daniel',
    'Sebastián', 'Miguel', 'Rafael', 'Fernando', 'Juan', 'Alejandro',
    'Óscar', 'Ricardo', 'Eduardo', 'Héctor', 'Wilmer', 'Jhonatan', 'Cristian',
]

NOMBRES_FEM = [
    'María', 'Ana', 'Andrea', 'Sofía', 'Camila', 'Valentina', 'Gabriela',
    'Laura', 'Patricia', 'Luisa', 'Carmen', 'Daniela', 'Fernanda', 'Karina',
    'Génesis', 'Yessica', 'Adriana', 'Mariana', 'Ingrid', 'Natalia',
]

APELLIDOS = [
    'Pérez', 'González', 'Rodríguez', 'Martínez', 'Hernández', 'López',
    'García', 'Fernández', 'Sánchez', 'Ramírez', 'Torres', 'Flores',
    'Rivera', 'Gómez', 'Díaz', 'Vargas', 'Castro', 'Morales', 'Jiménez', 'Reyes',
]

PREFIJOS_TEL = ['0412', '0414', '0416', '0424', '0426']

DIRECCIONES_MARACAIBO = [
    'Av. 5 de Julio, Edif. Las Brisas, Apto 3B, Maracaibo, Zulia',
    'Calle 72 con Av. 15, Urb. La Lago, Casa 12, Maracaibo, Zulia',
    'Sector Tierra Negra, Calle 88, N° 15-40, Maracaibo, Zulia',
    'Urb. Santa Rita, Calle 10, Casa 5, Maracaibo, Zulia',
    'Av. Bella Vista, CC Lago Mall, Piso 2, Maracaibo, Zulia',
    'Urb. Las Mercedes, Calle 11, Casa 3, San Francisco, Zulia',
    'Parroquia Coquivacoa, Av. 13, N° 76-45, Maracaibo, Zulia',
    'Av. Universidad, Edif. El Milagro, Piso 4, Maracaibo, Zulia',
    'Urb. Valle Frío, Calle Principal, Casa 9, Maracaibo, Zulia',
    'Sector Los Olivos, Manzana 4, Casa 16, Maracaibo, Zulia',
]

DIRECCIONES_OTRAS = [
    'Av. Francisco de Miranda, Chacao, Caracas, Distrito Capital',
    'Calle Valencia Centro, Av. Bolívar, Valencia, Carabobo',
    'Av. Las Delicias, Maracay, Aragua',
    'Urb. La Isabelica, Bloque 5, Apto 12, Valencia, Carabobo',
    'Av. Principal El Rosal, Torre Seguros Caracas, Caracas',
    'Calle Bermúdez, Maturín, Monagas',
    'Av. Los Próceres, Barquisimeto, Lara',
    'Sector El Ujano, Urb. Agua Viva, Barquisimeto, Lara',
    'Calle Urdaneta, El Tigre, Anzoátegui',
    'Av. Gran Mariscal, Puerto Ordaz, Bolívar',
]

BANCOS_SUDEBAN = [
    ('0102', 'Banco de Venezuela'),
    ('0105', 'Mercantil'),
    ('0108', 'BBVA Provincial'),
    ('0114', 'Bancaribe'),
    ('0134', 'Banesco'),
    ('0151', 'BFC Banco Fondo Común'),
    ('0156', '100% Banco'),
    ('0163', 'Banco del Tesoro'),
    ('0172', 'Bancamiga'),
    ('0174', 'Banplus'),
    ('0175', 'Bicentenario'),
    ('0191', 'BNC Nacional de Crédito'),
]

MOTIVOS_RECHAZO = [
    'Comprobante ilegible, no se puede verificar la referencia.',
    'Referencia no encontrada en el banco emisor.',
    'Monto del comprobante no coincide con el monto declarado.',
    'Comprobante vencido, fecha de operación fuera del rango permitido.',
]

EQUIPOS_RIVALES = [
    'Deportivo Rayo Zuliano', 'Zulia FC Sub', 'Academia José Antonio Páez',
    'Unión Atlético Maracaibo', 'Fundación Zulia Fútbol', 'Titanes FC',
    'Asociación Zulia Elite', 'Atlético San Francisco', 'Deportivo La Popular',
    'UAV Maracaibo Sub',
]


def _cedula_al_azar(cedulas_existentes):
    while True:
        num = random.randint(10000000, 32000000)
        ci = f"V-{num}"
        if ci not in cedulas_existentes:
            cedulas_existentes.add(ci)
            return ci


def _telefono():
    prefijo = random.choice(PREFIJOS_TEL)
    numero = ''.join([str(random.randint(0, 9)) for _ in range(7)])
    return f"{prefijo}{numero}"


def _direccion():
    pool = DIRECCIONES_MARACAIBO * 3 + DIRECCIONES_OTRAS
    return random.choice(pool)


def _nombres_al_azar(masculino=True):
    n = random.choice(NOMBRES_MASC if masculino else NOMBRES_FEM)
    a1 = random.choice(APELLIDOS)
    a2 = random.choice(APELLIDOS)
    while a2 == a1:
        a2 = random.choice(APELLIDOS)
    return n, f"{a1} {a2}"


def _fecha_nacimiento_en_categoria(nombre_cat, anio_ref):
    edades = {
        'Sub-5': (4, 5), 'Sub-7': (6, 7), 'Sub-9': (8, 9),
        'Sub-11': (10, 11), 'Sub-13': (12, 13), 'Sub-15': (14, 15),
    }
    rango = edades.get(nombre_cat, (8, 11))
    edad = random.randint(rango[0], rango[1])
    anio = anio_ref - edad
    mes = random.randint(1, 12)
    dia = random.randint(1, 28)
    return datetime.date(anio, mes, dia)


def _fecha_pasada(dias_min=1, dias_max=180):
    delta = random.randint(dias_min, dias_max)
    return timezone.now().date() - datetime.timedelta(days=delta)


def _datetime_pasado(dias_min=1, dias_max=180):
    delta = random.randint(dias_min, dias_max)
    return timezone.now() - datetime.timedelta(days=delta)


def _comprobante_dummy(referencia):
    img = Image.new('RGB', (400, 200), color=(240, 240, 240))
    buffer = io.BytesIO()
    img.save(buffer, format='PNG')
    return ContentFile(buffer.getvalue(), name=f'comprobante_{referencia}.png')


class Command(BaseCommand):
    help = 'Siembra la base de datos con datos de prueba venezolanos realistas para FDM.'

    def add_arguments(self, parser):
        parser.add_argument('--clean', action='store_true', help='Elimina datos de prueba anteriores.')
        parser.add_argument('--flush', action='store_true', help='Limpia TODA la base de datos antes de sembrar.')
        parser.add_argument('--atletas', type=int, default=30, help='Número de atletas a sembrar.')
        parser.add_argument('--password', type=str, default='Fdm2026*', help='Contraseña para usuarios demo.')
        parser.add_argument('--verbose', action='store_true', help='Muestra logs detallados.')

    def handle(self, *args, **options):
        self._verbose = options['verbose']
        self._n_atletas = options['atletas']
        self._password = options['password']

        if options['flush']:
            if not settings.DEBUG:
                raise CommandError('--flush está bloqueado en modo producción (DEBUG=False).')
            self.stdout.write('[WARNING] --flush activado: Limpiando base de datos completa...')
            call_command('flush', verbosity=0, interactive=False)

        elif options['clean']:
            self.stdout.write('  [CLEAN] Eliminando datos de prueba anteriores...')
            self._limpiar_datos_seed()

        self.stdout.write(self.style.SUCCESS('[START] Iniciando seed FDM...'))
        with transaction.atomic():
            self._run_seed()

    def _limpiar_datos_seed(self):
        EvaluacionTecnica.objects.filter(entrenador__telefono__startswith='SEED_').delete()
        EvaluacionPsicosocial.objects.filter(evaluador__telefono__startswith='SEED_').delete()
        Estadistica.objects.filter(partido__equipo_rival__startswith='[SEED]').delete()
        Partido.objects.filter(equipo_rival__startswith='[SEED]').delete()
        PagoAuditLog.objects.filter(pago__concepto__startswith='[SEED]').delete()
        Mensualidad.objects.filter(atleta__representante__correo_electronico__endswith='@seed.fdm.local').delete()
        Pago.objects.filter(concepto__startswith='[SEED]').delete()
        Atleta.objects.filter(representante__correo_electronico__endswith='@seed.fdm.local').delete()
        Representante.objects.filter(correo_electronico__endswith='@seed.fdm.local').delete()
        CategoriaEntrenadores.objects.filter(personal__telefono__startswith='SEED_').delete()
        Categoria.objects.filter(coordinador_supervisor__telefono__startswith='SEED_').delete()
        Personal.objects.filter(telefono__startswith='SEED_').delete()
        User.objects.filter(username__startswith='seed_', is_superuser=False).delete()
        User.objects.filter(username='admin_seed').delete()
        TasaBCV.objects.filter(fuente='seed').delete()

    def _run_seed(self):
        hoy = timezone.now().date()
        anio_ref = hoy.year
        password = self._password
        n_atletas = self._n_atletas

        # ── 1. Sembrar Catálogos Base (3NF) ──────────────────────────────
        cargo_gen, _ = CAT_Cargo.objects.get_or_create(nombre='General', defaults={'descripcion': 'Coordinación General'})
        cargo_dep, _ = CAT_Cargo.objects.get_or_create(nombre='Deportivo', defaults={'descripcion': 'Coordinación Deportiva'})
        cargo_tes, _ = CAT_Cargo.objects.get_or_create(nombre='Tesoreria', defaults={'descripcion': 'Personal de Tesorería'})
        cargo_ent, _ = CAT_Cargo.objects.get_or_create(nombre='Entrenador', defaults={'descripcion': 'Personal Técnico'})
        cargo_del, _ = CAT_Cargo.objects.get_or_create(nombre='Delegado', defaults={'descripcion': 'Delegado de Categoría'})

        lic_fvf, _ = CAT_Licencia.objects.get_or_create(nombre='Licencia FVF')
        lic_conmebol, _ = CAT_Licencia.objects.get_or_create(nombre='Licencia CONMEBOL')

        gen_masc, _ = CAT_Genero.objects.get_or_create(nombre='Masculino')
        gen_fem, _ = CAT_Genero.objects.get_or_create(nombre='Femenino')
        gen_mix, _ = CAT_Genero.objects.get_or_create(nombre='Mixto')

        pos_por, _ = CAT_Posicion.objects.get_or_create(codigo='POR', defaults={'nombre': 'Portero'})
        pos_def, _ = CAT_Posicion.objects.get_or_create(codigo='DEF', defaults={'nombre': 'Defensa'})
        pos_med, _ = CAT_Posicion.objects.get_or_create(codigo='MED', defaults={'nombre': 'Mediocampista'})
        pos_del, _ = CAT_Posicion.objects.get_or_create(codigo='DEL', defaults={'nombre': 'Delantero'})
        posiciones_list = [pos_por, pos_def, pos_med, pos_del]

        lat_der, _ = CAT_Lateralidad.objects.get_or_create(nombre='Derecho')
        lat_izq, _ = CAT_Lateralidad.objects.get_or_create(nombre='Izquierdo')
        lat_amb, _ = CAT_Lateralidad.objects.get_or_create(nombre='Ambidiestro')
        lateralidades_list = [lat_der, lat_izq, lat_amb]

        tipo_am, _ = CAT_TipoPartido.objects.get_or_create(codigo='AMISTOSO', defaults={'nombre': 'Amistoso'})
        tipo_of, _ = CAT_TipoPartido.objects.get_or_create(codigo='OFICIAL', defaults={'nombre': 'Oficial'})

        cond_casa, _ = CAT_CondicionPartido.objects.get_or_create(codigo='CASA', defaults={'nombre': 'Casa'})
        cond_vis, _ = CAT_CondicionPartido.objects.get_or_create(codigo='VISITANTE', defaults={'nombre': 'Visitante'})

        bancos_dict = {}
        for cod, nom in BANCOS_SUDEBAN:
            b_obj, _ = CAT_Banco.objects.get_or_create(codigo_sudeban=cod, defaults={'nombre': nom, 'activo': True})
            bancos_dict[cod] = b_obj

        est_pen, _ = CAT_EstadoPago.objects.get_or_create(codigo='PENDIENTE', defaults={'descripcion': 'Pago reportado'})
        est_apr, _ = CAT_EstadoPago.objects.get_or_create(codigo='APROBADO', defaults={'descripcion': 'Pago verificado'})
        est_rec, _ = CAT_EstadoPago.objects.get_or_create(codigo='RECHAZADO', defaults={'descripcion': 'Pago rechazado'})

        met_pm, _ = CAT_MetodoPago.objects.get_or_create(codigo='PAGO_MOVIL', defaults={'nombre': 'Pago Móvil'})
        met_tr, _ = CAT_MetodoPago.objects.get_or_create(codigo='TRANSFERENCIA', defaults={'nombre': 'Transferencia'})
        met_eb, _ = CAT_MetodoPago.objects.get_or_create(codigo='EFECTIVO_BS', defaults={'nombre': 'Efectivo Bs'})
        met_eu, _ = CAT_MetodoPago.objects.get_or_create(codigo='EFECTIVO_USD', defaults={'nombre': 'Efectivo USD'})
        metodos_list = [met_pm, met_tr, met_eb, met_eu]

        # ── 2. TasaBCV ───────────────────────────────────────────────────
        tasa_bcv, _ = TasaBCV.objects.get_or_create(
            fecha=hoy,
            defaults={'tasa': Decimal('36.50'), 'fuente': 'seed'},
        )

        # ── 3. Superusuario admin_seed ───────────────────────────────────
        if not User.objects.filter(username='admin_fdm').exists():
            admin, creado = User.objects.get_or_create(
                username='admin_seed',
                defaults={
                    'email': 'admin_seed@seed.fdm.local',
                    'is_superuser': True,
                    'is_staff': True,
                    'first_name': 'Admin',
                    'last_name': 'Seed',
                },
            )
            if creado:
                admin.set_password(password)
                admin.save()

        # ── 4. Grupos RBAC ───────────────────────────────────────────────
        grupo_cg, _ = Group.objects.get_or_create(name='CoordinadorGeneral')
        grupo_cd, _ = Group.objects.get_or_create(name='CoordinadorDeportivo')
        grupo_tes, _ = Group.objects.get_or_create(name='Tesoreria')

        # ── 5. Personal: Coordinadores y Tesorería ───────────────────────
        user_cg, _ = User.objects.get_or_create(
            username='seed_coord_general',
            defaults={'email': 'seed_coord_general@seed.fdm.local', 'is_staff': True, 'first_name': 'Roberto', 'last_name': 'Medina'}
        )
        user_cg.set_password(password)
        user_cg.save()
        user_cg.groups.add(grupo_cg)

        coord_general, _ = Personal.objects.get_or_create(
            cedula_identidad='V-SEED-001',
            defaults={'usuario': user_cg, 'cargo': cargo_gen, 'nombres': 'Roberto Carlos', 'apellidos': 'Medina Pérez', 'telefono': 'SEED_0412001', 'activo': True}
        )

        user_cde, _ = User.objects.get_or_create(
            username='seed_coord_deportivo',
            defaults={'email': 'seed_coord_deportivo@seed.fdm.local', 'is_staff': True, 'first_name': 'Andrés', 'last_name': 'Villalobos'}
        )
        user_cde.set_password(password)
        user_cde.save()
        user_cde.groups.add(grupo_cd)

        coord_deportivo, _ = Personal.objects.get_or_create(
            cedula_identidad='V-SEED-002',
            defaults={'usuario': user_cde, 'cargo': cargo_dep, 'nombres': 'Andrés Felipe', 'apellidos': 'Villalobos Torres', 'telefono': 'SEED_0412002', 'activo': True}
        )

        user_tes, _ = User.objects.get_or_create(
            username='seed_tesoreria',
            defaults={'email': 'seed_tesoreria@seed.fdm.local', 'is_staff': True, 'first_name': 'Luisa', 'last_name': 'Ferrer'}
        )
        user_tes.set_password(password)
        user_tes.save()
        user_tes.groups.add(grupo_tes)

        personal_tesoreria, _ = Personal.objects.get_or_create(
            cedula_identidad='V-SEED-003',
            defaults={'usuario': user_tes, 'cargo': cargo_tes, 'nombres': 'Luisa', 'apellidos': 'Ferrer', 'telefono': 'SEED_0412003', 'activo': True}
        )

        # ── 6. Entrenadores y Delegados (Personal) ───────────────────────
        entrenadores_data = [
            ('Freddy', 'Urdaneta Morales', lic_fvf, 'SEED_0412000001', 'V-SEED-101'),
            ('Héctor', 'Bracho Sánchez', lic_conmebol, 'SEED_0416000002', 'V-SEED-102'),
            ('Wilmer', 'Chirinos Díaz', lic_fvf, 'SEED_0424000003', 'V-SEED-103'),
            ('José Luis', 'Rincón González', lic_conmebol, 'SEED_0414000004', 'V-SEED-104'),
        ]
        entrenadores = []
        for nombres, apellidos, licencia, tel, ci in entrenadores_data:
            p_ent, _ = Personal.objects.get_or_create(
                cedula_identidad=ci,
                defaults={'cargo': cargo_ent, 'licencia': licencia, 'nombres': nombres, 'apellidos': apellidos, 'telefono': tel, 'activo': True}
            )
            entrenadores.append(p_ent)

        delegados_data = [
            ('Carmen', 'Fuenmayor López', 'SEED_0412000005', 'V-SEED-201'),
            ('Xiomara', 'Palmar Ríos', 'SEED_0424000006', 'V-SEED-202'),
            ('Gladys', 'Pérez Marín', 'SEED_0416000007', 'V-SEED-203'),
            ('Teresa', 'Méndez Bravo', 'SEED_0414000008', 'V-SEED-204'),
            ('Beatriz', 'Salazar Orozco', 'SEED_0426000009', 'V-SEED-205'),
            ('Victoria', 'Giménez Paz', 'SEED_0412000010', 'V-SEED-206'),
        ]
        delegados = []
        for nombres, apellidos, tel, ci in delegados_data:
            p_del, _ = Personal.objects.get_or_create(
                cedula_identidad=ci,
                defaults={'cargo': cargo_del, 'nombres': nombres, 'apellidos': apellidos, 'telefono': tel, 'activo': True}
            )
            delegados.append(p_del)

        # ── 7. Categorías ────────────────────────────────────────────────
        categorias_def = [
            ('Sub-5', anio_ref - 5, anio_ref - 4),
            ('Sub-7', anio_ref - 7, anio_ref - 6),
            ('Sub-9', anio_ref - 9, anio_ref - 8),
            ('Sub-11', anio_ref - 11, anio_ref - 10),
            ('Sub-13', anio_ref - 13, anio_ref - 12),
            ('Sub-15', anio_ref - 15, anio_ref - 14),
        ]
        categorias = []
        for idx, (nombre, anio_min, anio_max) in enumerate(categorias_def):
            delegado_cat = delegados[idx]
            cat, _ = Categoria.objects.get_or_create(
                nombre=nombre,
                defaults={
                    'anio_nacimiento_min': anio_min,
                    'anio_nacimiento_max': anio_max,
                    'genero': gen_masc,
                    'delegado': delegado_cat,
                    'coordinador_supervisor': coord_deportivo,
                },
            )
            ent_cat = entrenadores[idx % len(entrenadores)]
            CategoriaEntrenadores.objects.get_or_create(categoria=cat, personal=ent_cat)
            categorias.append(cat)

        # ── 8. Representantes ────────────────────────────────────────────
        cedulas_usadas = set(Representante.objects.values_list('cedula_identidad', flat=True))
        representantes = []
        for i in range(1, n_atletas + 1):
            username = f'seed_rep_{i:03d}'
            correo = f'{username}@seed.fdm.local'
            cedula = _cedula_al_azar(cedulas_usadas)
            nombres, apellidos = _nombres_al_azar(masculino=random.random() > 0.5)

            user_rep, _ = User.objects.get_or_create(
                username=username,
                defaults={'email': correo, 'is_staff': False, 'first_name': nombres.split()[0], 'last_name': apellidos.split()[0]}
            )
            user_rep.set_password(password)
            user_rep.save()

            rep, _ = Representante.objects.get_or_create(
                cedula_identidad=cedula,
                defaults={
                    'nombres': nombres,
                    'apellidos': apellidos,
                    'telefono_principal': _telefono(),
                    'direccion_habitacion': _direccion(),
                    'correo_electronico': correo,
                    'usuario': user_rep,
                }
            )
            representantes.append(rep)

        # ── 9. Atletas ───────────────────────────────────────────────────
        atletas = []
        n_cats = len(categorias)
        for idx, rep in enumerate(representantes):
            cat = categorias[idx % n_cats]
            nombres_a, apellidos_a = _nombres_al_azar(masculino=True)
            fecha_nac = _fecha_nacimiento_en_categoria(cat.nombre, anio_ref)
            becado = (idx % 10 == 0)
            inactivo = (idx % 20 == 0)

            edad = hoy.year - fecha_nac.year - ((hoy.month, hoy.day) < (fecha_nac.month, fecha_nac.day))
            ci_atleta = f"V-{random.randint(33000000, 39000000)}" if edad >= 9 else None

            atleta, _ = Atleta.objects.get_or_create(
                representante=rep,
                nombres=nombres_a,
                apellidos=apellidos_a,
                defaults={
                    'categoria': cat,
                    'fecha_nacimiento': fecha_nac,
                    'posicion': random.choice(posiciones_list),
                    'lateralidad': random.choice(lateralidades_list),
                    'numero_acta_nacimiento': f"ACTA-{idx+1000}",
                    'cedula_identidad': ci_atleta,
                    'peso_kg': Decimal(str(round(random.uniform(20, 65), 1))),
                    'altura_mts': Decimal(str(round(random.uniform(1.10, 1.70), 2))),
                    'activo': not inactivo,
                    'becado': becado,
                }
            )
            atletas.append(atleta)

        # ── 10. Mensualidades ────────────────────────────────────────────
        for delta in range(2, -1, -1):
            if hoy.month - delta <= 0:
                m_rel, a_rel = hoy.month - delta + 12, hoy.year - 1
            else:
                m_rel, a_rel = hoy.month - delta, hoy.year
            call_command('generar_mensualidades', mes=m_rel, anio=a_rel, monto='15', verbosity=0)

        # ── 11. Pagos ────────────────────────────────────────────────────
        ids_atletas = [a.id for a in atletas]
        mensualidades = list(Mensualidad.objects.filter(atleta_id__in=ids_atletas, atleta__activo=True, atleta__becado=False))

        ref_cnt = 0
        for atleta_obj in atletas:
            ms = [m for m in mensualidades if m.atleta_id == atleta_obj.id and not m.esta_pagada]
            if not ms:
                continue
            ref_cnt += 1
            ref = f"SEED{ref_cnt:08d}"
            monto_u = sum(m.monto_usd for m in ms[:2])
            monto_b = (monto_u * tasa_bcv.tasa).quantize(Decimal('0.01'))

            pago = Pago.objects.create(
                representante=atleta_obj.representante,
                concepto=f"[SEED] Pago Mensualidad {atleta_obj.nombres}",
                metodo=random.choice(metodos_list),
                banco_emisor=random.choice(list(bancos_dict.values())),
                referencia=ref,
                monto_bs=monto_b,
                tasa_bcv=tasa_bcv.tasa,
                fecha_pago=_fecha_pasada(1, 60),
                estado=est_apr,
                revisado_por=user_tes,
                revisado_en=timezone.now()
            )
            for m in ms[:2]:
                m.pago = pago
                m.save()

            pago.registrar_audit('APROBADO', actor=user_tes, estado_anterior='PENDIENTE', estado_nuevo='APROBADO')

        # ── 12. Partidos y Estadísticas ──────────────────────────────────
        for i in range(1, 5):
            cat = categorias[i % n_cats]
            rival = f"[SEED] {random.choice(EQUIPOS_RIVALES)}"
            partido = Partido.objects.create(
                categoria=cat,
                equipo_rival=rival,
                tipo=tipo_am,
                condicion=cond_casa,
                fecha_hora=_datetime_pasado(5, 60),
                goles_favor_escuela=random.randint(1, 4),
                goles_contra_rival=random.randint(0, 2),
                procesado=True
            )
            atletas_cat = [a for a in atletas if a.categoria_id == cat.id]
            for atl in atletas_cat[:5]:
                Estadistica.objects.create(
                    atleta=atl,
                    partido=partido,
                    es_titular=True,
                    minutos_jugados=70,
                    goles=random.randint(0, 2),
                    asistencias=1,
                    calificacion_dt=Decimal('8.5')
                )

        # ── 13. Evaluaciones ─────────────────────────────────────────────
        for atl in atletas[:5]:
            ent = entrenadores[0]
            EvaluacionTecnica.objects.create(
                atleta=atl,
                entrenador=ent,
                fecha_evaluacion=_fecha_pasada(5, 30),
                control_balon=Decimal('8.0'),
                conduccion=Decimal('7.5'),
                pase_corto=Decimal('8.5'),
                tiro=Decimal('7.0'),
                inteligencia_tactica=Decimal('8.0'),
                observaciones='Buen desempeño técnico.'
            )
            EvaluacionPsicosocial.objects.create(
                atleta=atl,
                evaluador=coord_deportivo,
                fecha_evaluacion=_fecha_pasada(5, 30),
                compromiso=Decimal('9.0'),
                puntualidad=Decimal('9.5'),
                companerismo=Decimal('9.0'),
                respeto=Decimal('9.5'),
                manejo_frustracion=Decimal('8.0'),
                observaciones_conductuales='Excelente conducta e integración.'
            )

        self.stdout.write(self.style.SUCCESS('[SUCCESS] Seed FDM refactorizado en 3NF completado exitosamente.'))
