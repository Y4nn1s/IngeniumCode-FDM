# core/management/commands/seed_fdm.py
"""
Comando de gestión: seed_fdm
Crea datos de prueba venezolanos realistas para la plataforma FDM.

Convenciones de identificación seed (usadas por --reset):
  - Users seed        : username empieza con 'seed_'
  - Representantes    : correo_electronico termina en '@seed.fdm.local'
  - Coordinadores     : usuario_sistema.username empieza con 'seed_'
  - Entrenadores      : correo identificado por teléfono con sufijo seed
                        → no aplica (Entrenador no tiene correo);
                        se identifica por telefono__startswith='SEED_'
                        (convención de este seed).
  - Delegados         : telefono__startswith='SEED_'
  - Pagos seed        : concepto empieza con '[SEED]'
  - Partidos seed     : equipo_rival empieza con '[SEED]'
  - TasaBCV seed      : fuente='seed'

NUNCA correr en producción (--flush lo bloquea si DEBUG=False).
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

from administracion.models import Coordinador, Entrenador, Delegado, Categoria
from deportivo.models import Partido, Estadistica, EvaluacionTecnica, EvaluacionPsicosocial
from filiacion.models import Representante, Atleta
from finanzas.models import TasaBCV, Mensualidad, Pago, PagoAuditLog


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

BANCOS_PRINCIPALES = ['0102', '0134', '0172', '0105', '0108', '0174']
METODOS_PAGO = ['PAGO_MOVIL', 'TRANSFERENCIA', 'EFECTIVO_BS', 'EFECTIVO_USD']

MOTIVOS_RECHAZO = [
    'Comprobante ilegible, no se puede verificar la referencia.',
    'Referencia no encontrada en el banco emisor.',
    'Monto del comprobante no coincide con el monto declarado.',
    'Comprobante vencido, fecha de operación fuera del rango permitido.',
    'Referencia duplicada, ya fue utilizada en otro pago.',
    'El banco emisor no coincide con el seleccionado.',
]

OBSERVACIONES_TECNICAS = [
    'Buen rendimiento en los entrenamientos. Mejora continua.',
    'Debe trabajar la resistencia en tramos largos.',
    'Excelente control del balón, potencial destacado.',
    'Necesita mejorar la comunicación con compañeros.',
    'Gran capacidad táctica para su edad.',
    'Se recomienda reforzar el pase corto en situación de presión.',
    'Atleta disciplinado, asiste con puntualidad a todos los entrenamientos.',
]

OBSERVACIONES_PSICOSOCIALES = [
    'Muestra liderazgo positivo dentro del equipo.',
    'Se integra bien con el grupo, colaborador nato.',
    'Trabaja en el manejo de la frustración en situaciones adversas.',
    'Muy respetuoso con entrenadores y compañeros.',
    'Requiere acompañamiento para mejorar la autoconfianza.',
    'Excelente actitud, sirve de ejemplo para el resto del grupo.',
]

EQUIPOS_RIVALES = [
    'FC Academia Zulia', 'Deportivo Lago', 'Maracaibo FC',
    'Escuela Futbol Táchira', 'CD Los Gigantes', 'Academia Bolívar',
    'FC Juventud Maracaibo', 'Deportivo Caracas Juvenil',
]

# ─────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────

def _nombres_al_azar(masculino=True):
    """Retorna (nombres_str, apellidos_str) aleatorios venezolanos."""
    pool = NOMBRES_MASC if masculino else NOMBRES_FEM
    nombres = f"{random.choice(pool)} {random.choice(pool)}"
    apellidos = f"{random.choice(APELLIDOS)} {random.choice(APELLIDOS)}"
    return nombres, apellidos


def _cedula_al_azar(usadas):
    """Genera una cédula venezolana de 7-9 dígitos única."""
    while True:
        digitos = random.randint(7, 9)
        minimo = 10 ** (digitos - 1)
        maximo = (10 ** digitos) - 1
        cedula = str(random.randint(minimo, maximo))
        if cedula not in usadas:
            usadas.add(cedula)
            return cedula


def _telefono():
    """Genera número de teléfono venezolano."""
    prefijo = random.choice(PREFIJOS_TEL)
    cuerpo = str(random.randint(1000000, 9999999))
    return f"{prefijo}{cuerpo}"


def _direccion():
    """Genera dirección: ~70% Maracaibo, ~30% otras ciudades."""
    if random.random() < 0.70:
        return random.choice(DIRECCIONES_MARACAIBO)
    return random.choice(DIRECCIONES_OTRAS)


def _comprobante_dummy(ref):
    """Genera un PNG gris mínimo de 100×100 px en memoria. Retorna ContentFile."""
    img = Image.new('RGB', (100, 100), color=(128, 128, 128))
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    return ContentFile(buf.getvalue())


def _fecha_nacimiento_en_categoria(categoria_nombre, anio_ref):
    """
    Genera una fecha de nacimiento coherente con el rango de la categoría.
    anio_ref: año actual de referencia.
    """
    rangos = {
        'Sub-5':  (4, 5),
        'Sub-7':  (6, 7),
        'Sub-9':  (8, 9),
        'Sub-11': (10, 11),
        'Sub-13': (12, 13),
        'Sub-15': (14, 15),
    }
    edad_min, edad_max = rangos.get(categoria_nombre, (10, 15))
    anio_nac_min = anio_ref - edad_max
    anio_nac_max = anio_ref - edad_min
    anio = random.randint(anio_nac_min, anio_nac_max)
    mes = random.randint(1, 12)
    import calendar as cal
    ultimo_dia = cal.monthrange(anio, mes)[1]
    dia = random.randint(1, ultimo_dia)
    return datetime.date(anio, mes, dia)


def _fecha_pasada(dias_min=30, dias_max=365):
    """Retorna un date en el pasado."""
    dias = random.randint(dias_min, dias_max)
    return (timezone.now() - datetime.timedelta(days=dias)).date()


def _datetime_pasado(dias_min=1, dias_max=60):
    """Retorna un datetime naive en el pasado para revisado_en."""
    dias = random.randint(dias_min, dias_max)
    return timezone.now() - datetime.timedelta(days=dias)


# ─────────────────────────────────────────────
# Clase del comando
# ─────────────────────────────────────────────

class Command(BaseCommand):
    help = (
        'Crea datos de prueba venezolanos realistas para la plataforma FDM. '
        'NUNCA correr en producción.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--reset',
            action='store_true',
            help=(
                'Borra solo entidades seed (identificadas por prefijo seed_/ '
                'convenciones de seed) antes de crear. NUNCA toca superusers reales.'
            ),
        )
        parser.add_argument(
            '--flush',
            action='store_true',
            help=(
                'Equivale a flush + seed completo. '
                'Bloqueado si DEBUG=False.'
            ),
        )
        parser.add_argument(
            '--atletas',
            type=int,
            default=30,
            metavar='N',
            help='Número total de atletas a crear (default: 30).',
        )
        parser.add_argument(
            '--password',
            type=str,
            default='Demo1234*',
            metavar='PWD',
            help='Contraseña para todos los usuarios seed (default: Demo1234*).',
        )
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Output detallado de cada entidad creada.',
        )

    # ──────────────────────────────────────────
    # Punto de entrada principal
    # ──────────────────────────────────────────

    def handle(self, *args, **options):
        self._verbose = options['verbose']
        self._password = options['password']
        self._n_atletas = options['atletas']

        # Bloqueo de --flush en producción
        if options['flush'] and not settings.DEBUG:
            raise CommandError(
                '⛔  --flush está BLOQUEADO en producción (DEBUG=False). '
                'Usa este comando solo en entornos de desarrollo.'
            )

        if options['flush']:
            self._log('⚙️  --flush: ejecutando flush de base de datos...', always=True)
            call_command('flush', '--no-input', verbosity=0)
            self._log('✓ Base de datos vaciada.', always=True)

        if options['reset'] and not options['flush']:
            self._log('♻️  --reset: eliminando datos seed anteriores...', always=True)
            with transaction.atomic():
                self._reset()
            self._log('✓ Reset completado.', always=True)

        self._log('🌱 Iniciando seed FDM...', always=True)

        with transaction.atomic():
            self._run_seed()

    # ──────────────────────────────────────────
    # Reset: borrado ordenado respetando FK
    # ──────────────────────────────────────────

    def _reset(self):
        # 1. PagoAuditLog de pagos seed
        logs_borrados = PagoAuditLog.objects.filter(
            pago__concepto__startswith='[SEED]'
        ).delete()[0]
        self._log(f'  - {logs_borrados} PagoAuditLog eliminados')

        # 2. Pagos seed
        pagos_borrados = Pago.objects.filter(
            concepto__startswith='[SEED]'
        ).delete()[0]
        self._log(f'  - {pagos_borrados} Pagos eliminados')

        # 3. Mensualidades de atletas de representantes seed
        mensualidades_borradas = Mensualidad.objects.filter(
            atleta__representante__usuario__username__startswith='seed_rep_'
        ).delete()[0]
        self._log(f'  - {mensualidades_borradas} Mensualidades eliminadas')

        # 4. Estadísticas de partidos seed
        estadisticas_borradas = Estadistica.objects.filter(
            partido__equipo_rival__startswith='[SEED]'
        ).delete()[0]
        self._log(f'  - {estadisticas_borradas} Estadísticas eliminadas')

        # 5. EvaluacionTecnica y EvaluacionPsicosocial de atletas seed
        et_borradas = EvaluacionTecnica.objects.filter(
            atleta__representante__usuario__username__startswith='seed_rep_'
        ).delete()[0]
        ep_borradas = EvaluacionPsicosocial.objects.filter(
            atleta__representante__usuario__username__startswith='seed_rep_'
        ).delete()[0]
        self._log(f'  - {et_borradas} EvaluacionTecnica eliminadas')
        self._log(f'  - {ep_borradas} EvaluacionPsicosocial eliminadas')

        # 6. Atletas de representantes seed
        atletas_borrados = Atleta.objects.filter(
            representante__usuario__username__startswith='seed_rep_'
        ).delete()[0]
        self._log(f'  - {atletas_borrados} Atletas eliminados')

        # 7. Representantes seed
        reps_borrados = Representante.objects.filter(
            usuario__username__startswith='seed_rep_'
        ).delete()[0]
        self._log(f'  - {reps_borrados} Representantes eliminados')

        # 8. Users seed (excepto superusers reales)
        users_borrados = User.objects.filter(
            username__startswith='seed_',
            is_superuser=False,
        ).delete()[0]
        # también el admin_seed que sí es superuser pero es nuestro
        User.objects.filter(username='admin_seed').delete()
        self._log(f'  - {users_borrados} Users seed eliminados')

        # 9. Coordinadores seed (sus Users ya fueron borrados en cascada)
        # Los Coordinador están en CASCADE con User, se habrán borrado en cascada
        # pero por si acaso:
        Coordinador.objects.filter(
            usuario_sistema__username__startswith='seed_'
        ).delete()

        # 10. Entrenadores y Delegados seed (por teléfono convención)
        entrenadores_borrados = Entrenador.objects.filter(
            telefono__startswith='SEED_'
        ).delete()[0]
        delegados_borrados = Delegado.objects.filter(
            telefono__startswith='SEED_'
        ).delete()[0]
        self._log(f'  - {entrenadores_borrados} Entrenadores eliminados')
        self._log(f'  - {delegados_borrados} Delegados eliminados')

        # 11. Categorías SOLO si no tienen atletas
        for cat in Categoria.objects.filter(nombre__in=[
            'Sub-5', 'Sub-7', 'Sub-9', 'Sub-11', 'Sub-13', 'Sub-15'
        ]):
            if not cat.atletas.exists():
                cat.delete()
                self._log(f'  - Categoría {cat.nombre} eliminada')

        # 12. TasaBCV seed
        tasas_borradas = TasaBCV.objects.filter(fuente='seed').delete()[0]
        self._log(f'  - {tasas_borradas} TasaBCV seed eliminadas')

        # 13. Partidos seed
        partidos_borrados = Partido.objects.filter(
            equipo_rival__startswith='[SEED]'
        ).delete()[0]
        self._log(f'  - {partidos_borrados} Partidos seed eliminados')

    # ──────────────────────────────────────────
    # Seed principal
    # ──────────────────────────────────────────

    def _run_seed(self):
        hoy = timezone.now().date()
        anio_ref = hoy.year
        password = self._password
        n_atletas = self._n_atletas

        contadores = {
            'superusers': 0,
            'coordinadores': 0,
            'tesoreria': 0,
            'entrenadores': 0,
            'delegados': 0,
            'categorias': 0,
            'representantes': 0,
            'atletas': 0,
            'atletas_becados': 0,
            'atletas_inactivos': 0,
            'mensualidades': 0,
            'pagos_aprobados': 0,
            'pagos_pendientes': 0,
            'pagos_rechazados': 0,
            'tasa_bcv': 0,
            'partidos': 0,
            'estadisticas': 0,
            'evaluaciones_tecnicas': 0,
            'evaluaciones_psicosociales': 0,
        }

        cedulas_usadas = set(
            Representante.objects.values_list('cedula_identidad', flat=True)
        )

        # ── 1. TasaBCV ───────────────────────────────────────────────────
        tasa_bcv, creada = TasaBCV.objects.get_or_create(
            fecha=hoy,
            defaults={'tasa': Decimal('36.50'), 'fuente': 'seed'},
        )
        if creada:
            contadores['tasa_bcv'] = 1
            self._log(f'  ✓ TasaBCV creada: {hoy} @ 36.50 Bs/USD')
        else:
            self._log(f'  · TasaBCV ya existe para hoy ({tasa_bcv.tasa} Bs/USD)')

        # ── 2. Superusuario admin_seed ───────────────────────────────────
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
                contadores['superusers'] = 1
                self._log('  ✓ Superuser admin_seed creado')
            else:
                self._log('  · admin_seed ya existe')
        else:
            self._log('  · admin_fdm detectado — se omite creación de admin_seed')

        # ── 3. Grupos RBAC (ya existen por migración, solo obtener) ──────
        grupo_cg = Group.objects.get(name='CoordinadorGeneral')
        grupo_cd = Group.objects.get(name='CoordinadorDeportivo')
        grupo_tes = Group.objects.get(name='Tesoreria')

        # ── 4. Coordinador General ───────────────────────────────────────
        user_cg, creado = User.objects.get_or_create(
            username='seed_coord_general',
            defaults={
                'email': 'seed_coord_general@seed.fdm.local',
                'is_staff': True,
                'is_superuser': False,
                'first_name': 'Roberto',
                'last_name': 'Medina',
            },
        )
        if creado:
            user_cg.set_password(password)
            user_cg.save()
            user_cg.groups.add(grupo_cg)

        coord_general, creado = Coordinador.objects.get_or_create(
            usuario_sistema=user_cg,
            defaults={
                'nombres': 'Roberto Carlos',
                'apellidos': 'Medina Pérez',
                'cargo': 'GENERAL',
            },
        )
        if creado:
            contadores['coordinadores'] += 1
            self._log('  ✓ Coordinador General creado: Roberto Carlos Medina Pérez')

        # ── 5. Coordinador Deportivo ─────────────────────────────────────
        user_cde, creado = User.objects.get_or_create(
            username='seed_coord_deportivo',
            defaults={
                'email': 'seed_coord_deportivo@seed.fdm.local',
                'is_staff': True,
                'is_superuser': False,
                'first_name': 'Andrés',
                'last_name': 'Villalobos',
            },
        )
        if creado:
            user_cde.set_password(password)
            user_cde.save()
            user_cde.groups.add(grupo_cd)

        coord_deportivo, creado = Coordinador.objects.get_or_create(
            usuario_sistema=user_cde,
            defaults={
                'nombres': 'Andrés Felipe',
                'apellidos': 'Villalobos Torres',
                'cargo': 'DEPORTIVO',
            },
        )
        if creado:
            contadores['coordinadores'] += 1
            self._log('  ✓ Coordinador Deportivo creado: Andrés Felipe Villalobos Torres')

        # ── 6. Usuario Tesorería ─────────────────────────────────────────
        user_tes, creado = User.objects.get_or_create(
            username='seed_tesoreria',
            defaults={
                'email': 'seed_tesoreria@seed.fdm.local',
                'is_staff': True,
                'is_superuser': False,
                'first_name': 'Luisa',
                'last_name': 'Ferrer',
            },
        )
        if creado:
            user_tes.set_password(password)
            user_tes.save()
            user_tes.groups.add(grupo_tes)
            contadores['tesoreria'] = 1
            self._log('  ✓ Usuario Tesorería creado: seed_tesoreria')

        # ── 7. Entrenadores ──────────────────────────────────────────────
        entrenadores_data = [
            ('Freddy',  'Urdaneta Morales',  'FVF',      '0412', '3',  coord_deportivo),
            ('Héctor',  'Bracho Sánchez',    'CONMEBOL', '0416', '7',  coord_deportivo),
            ('Wilmer',  'Chirinos Díaz',     'FVF',      '0424', '1',  coord_deportivo),
            ('José Luis','Rincón González',  'CONMEBOL', '0414', '9',  coord_deportivo),
        ]
        entrenadores = []
        for nombres, apellidos, licencia, prefijo, sufijo, coord in entrenadores_data:
            tel = f"SEED_{prefijo}{sufijo * 7}"[:20]  # convención seed para reset
            entrenador, creado = Entrenador.objects.get_or_create(
                telefono=tel,
                defaults={
                    'nombres': nombres,
                    'apellidos': apellidos,
                    'licencia': licencia,
                    'coordinador': coord,
                    'activo': True,
                },
            )
            entrenadores.append(entrenador)
            if creado:
                contadores['entrenadores'] += 1
                self._log(f'  ✓ Entrenador: {nombres} {apellidos}')

        # ── 8. Delegados ─────────────────────────────────────────────────
        delegados_data = [
            ('Carmen',   'Fuenmayor López', 'SEED_04120000001'),
            ('Xiomara',  'Palmar Ríos',     'SEED_04240000002'),
            ('Gladys',   'Pérez Marín',     'SEED_04160000003'),
            ('Teresa',   'Méndez Bravo',    'SEED_04140000004'),
            ('Beatriz',  'Salazar Orozco',  'SEED_04260000005'),
            ('Victoria', 'Giménez Paz',     'SEED_04120000006'),
        ]
        delegados = []
        for nombres, apellidos, tel in delegados_data:
            delegado, creado = Delegado.objects.get_or_create(
                telefono=tel,
                defaults={'nombres': nombres, 'apellidos': apellidos},
            )
            delegados.append(delegado)
            if creado:
                contadores['delegados'] += 1
                self._log(f'  ✓ Delegado: {nombres} {apellidos}')

        # ── 9. Categorías ────────────────────────────────────────────────
        categorias_def = [
            ('Sub-5',  anio_ref - 5, anio_ref - 4),
            ('Sub-7',  anio_ref - 7, anio_ref - 6),
            ('Sub-9',  anio_ref - 9, anio_ref - 8),
            ('Sub-11', anio_ref - 11, anio_ref - 10),
            ('Sub-13', anio_ref - 13, anio_ref - 12),
            ('Sub-15', anio_ref - 15, anio_ref - 14),
        ]
        categorias = []
        for idx, (nombre, anio_min, anio_max) in enumerate(categorias_def):
            delegado_cat = delegados[idx]
            entrenadores_cat = entrenadores[idx * 2 // len(entrenadores_data)
                                           :idx * 2 // len(entrenadores_data) + 2]
            if not entrenadores_cat:
                entrenadores_cat = entrenadores[:2]

            cat, creada = Categoria.objects.get_or_create(
                nombre=nombre,
                defaults={
                    'anio_nacimiento_min': anio_min,
                    'anio_nacimiento_max': anio_max,
                    'genero': 'MASCULINO',
                    'delegado': delegado_cat,
                    'coordinador_supervisor': coord_deportivo,
                },
            )
            if creada:
                cat.entrenadores_asignados.set(entrenadores_cat)
                contadores['categorias'] += 1
                self._log(f'  ✓ Categoría: {nombre} ({anio_min}-{anio_max})')
            else:
                # Asegurar entrenadores aunque ya existiera
                if not cat.entrenadores_asignados.exists():
                    cat.entrenadores_asignados.set(entrenadores_cat)
            categorias.append(cat)

        # ── 10. Representantes y Users ───────────────────────────────────
        n_reps = n_atletas  # 1 rep puede tener 1-2 atletas; usamos mismo número
        representantes = []
        for i in range(1, n_reps + 1):
            username = f'seed_rep_{i:03d}'
            correo = f'{username}@seed.fdm.local'
            cedula = _cedula_al_azar(cedulas_usadas)
            nombres, apellidos = _nombres_al_azar(masculino=random.random() > 0.5)

            user_rep, creado_u = User.objects.get_or_create(
                username=username,
                defaults={
                    'email': correo,
                    'is_staff': False,
                    'is_superuser': False,
                    'first_name': nombres.split()[0],
                    'last_name': apellidos.split()[0],
                },
            )
            if creado_u:
                user_rep.set_password(password)
                user_rep.save()

            rep, creado_r = Representante.objects.get_or_create(
                cedula_identidad=cedula,
                defaults={
                    'nombres': nombres,
                    'apellidos': apellidos,
                    'telefono_principal': _telefono(),
                    'direccion_habitacion': _direccion(),
                    'correo_electronico': correo,
                    'telegram_chat_id': '',
                    'usuario': user_rep,
                },
            )
            # Si ya existe rep por esta cédula pero el user no está vinculado:
            if not creado_r and rep.usuario is None:
                rep.usuario = user_rep
                rep.save()

            representantes.append(rep)
            if creado_r:
                contadores['representantes'] += 1
                if creado_u:
                    self._log(f'  ✓ Representante {i:03d}: {nombres} {apellidos}')

        # ── 11. Atletas ──────────────────────────────────────────────────
        atletas = []
        posiciones = ['POR', 'DEF', 'MED', 'DEL']
        lateralidades = ['DERECHO', 'IZQUIERDO', 'AMBIDIESTRO']
        n_cats = len(categorias)

        atletas_por_rep = []
        # Distribuir atletas: algunos reps tienen 1 atleta, algunos 2
        # Total: n_atletas atletas entre n_reps representantes
        # Asignar 2 atletas a los primeros (n_atletas - n_reps) representantes
        # y 1 atleta a los demás
        extras = n_atletas - n_reps  # cuántos reps tendrán 2 atletas
        if extras < 0:
            extras = 0
        for i, rep in enumerate(representantes):
            count = 2 if i < extras else 1
            atletas_por_rep.append((rep, count))

        atleta_global_idx = 0
        for rep, count in atletas_por_rep:
            for j in range(count):
                if atleta_global_idx >= n_atletas:
                    break
                cat = categorias[atleta_global_idx % n_cats]
                nombres_a, apellidos_a = _nombres_al_azar(masculino=True)
                fecha_nac = _fecha_nacimiento_en_categoria(cat.nombre, anio_ref)
                becado = (atleta_global_idx % 10 == 0)     # ~10%
                inactivo = (atleta_global_idx % 20 == 0)   # ~5%
                # cedula escolar: string con prefijo E para unicidad
                cedula_esc = f"E{atleta_global_idx + 1:05d}"

                atleta, creado = Atleta.objects.get_or_create(
                    cedula_escolar=cedula_esc,
                    defaults={
                        'representante': rep,
                        'categoria': cat,
                        'nombres': nombres_a,
                        'apellidos': apellidos_a,
                        'fecha_nacimiento': fecha_nac,
                        'peso_kg': Decimal(str(round(random.uniform(20, 75), 1))),
                        'altura_mts': Decimal(str(round(random.uniform(1.10, 1.75), 2))),
                        'lateralidad': random.choice(lateralidades),
                        'posicion': random.choice(posiciones),
                        'activo': not inactivo,
                        'becado': becado,
                    },
                )
                atletas.append(atleta)
                if creado:
                    contadores['atletas'] += 1
                    if becado:
                        contadores['atletas_becados'] += 1
                    if inactivo:
                        contadores['atletas_inactivos'] += 1
                    self._log(
                        f'  ✓ Atleta {atleta_global_idx+1}: {nombres_a} '
                        f'({cat.nombre}, becado={becado}, activo={not inactivo})'
                    )
                atleta_global_idx += 1

        # ── 12. Mensualidades (via generar_mensualidades) ─────────────────
        self._log('  ⚙️  Generando mensualidades (3 meses)...', always=True)
        today = timezone.now().date()
        meses_a_generar = []
        for delta in range(2, -1, -1):  # mes actual y 2 anteriores
            if today.month - delta <= 0:
                mes_rel = today.month - delta + 12
                anio_rel = today.year - 1
            else:
                mes_rel = today.month - delta
                anio_rel = today.year
            meses_a_generar.append((mes_rel, anio_rel))

        for mes, anio in meses_a_generar:
            call_command(
                'generar_mensualidades',
                mes=mes,
                anio=anio,
                monto='15',
                verbosity=0,
            )
            self._log(f'  ✓ Mensualidades generadas: {mes}/{anio}')

        # Contar mensualidades seed (las de atletas seed)
        ids_atletas_seed = [a.id for a in atletas]
        total_mensualidades = Mensualidad.objects.filter(
            atleta_id__in=ids_atletas_seed
        ).count()
        contadores['mensualidades'] = total_mensualidades
        self._log(f'  ✓ Total mensualidades seed: {total_mensualidades}')

        # ── 13. Pagos ────────────────────────────────────────────────────
        self._log('  ⚙️  Creando pagos...', always=True)

        # Obtenemos mensualidades de atletas seed que NO están becados y activos
        mensualidades_seed = list(
            Mensualidad.objects.filter(
                atleta_id__in=ids_atletas_seed,
                atleta__activo=True,
                atleta__becado=False,
            ).select_related('atleta__representante').order_by('id')
        )

        # Agrupar por representante
        from collections import defaultdict
        menses_por_rep = defaultdict(list)
        for m in mensualidades_seed:
            menses_por_rep[m.atleta.representante_id].append(m)

        # Contador secuencial de referencias
        ref_contador = Pago.objects.filter(
            concepto__startswith='[SEED]'
        ).count()

        for rep_id, menses in menses_por_rep.items():
            rep = menses[0].atleta.representante

            # Dividir mensualidades en grupos de pago (1-3 mensualidades por pago)
            random.shuffle(menses)
            grupos = []
            while menses:
                tamaño = random.randint(1, min(3, len(menses)))
                grupos.append(menses[:tamaño])
                menses = menses[tamaño:]

            for grupo in grupos:
                ref_contador += 1
                referencia = f"SEED{ref_contador:08d}"
                monto_usd = sum(m.monto_usd for m in grupo)
                monto_bs = (monto_usd * tasa_bcv.tasa).quantize(Decimal('0.01'))

                metodo = random.choice(METODOS_PAGO)
                banco = random.choice(BANCOS_PRINCIPALES)

                # Determinar estado: 70% APROBADO, 15% PENDIENTE, 15% RECHAZADO
                rand = random.random()
                if rand < 0.70:
                    estado = 'APROBADO'
                elif rand < 0.85:
                    estado = 'PENDIENTE'
                else:
                    estado = 'RECHAZADO'

                fecha_pago = _fecha_pasada(1, 90)
                concepto_ids = ', '.join(
                    f"{m.periodo_mes}/{m.periodo_anio}" for m in grupo
                )
                concepto = f"[SEED] Mensualidad(es) {concepto_ids} - Rep. {rep.nombres}"

                # Revisar si ya existe pago seed con esta referencia
                if Pago.objects.filter(concepto__startswith='[SEED]',
                                       referencia=referencia).exists():
                    continue

                pago = Pago(
                    representante=rep,
                    concepto=concepto,
                    metodo=metodo,
                    banco_emisor=banco,
                    referencia=referencia,
                    monto_bs=monto_bs,
                    tasa_bcv=tasa_bcv.tasa,
                    fecha_pago=fecha_pago,
                    estado=estado,
                )

                # Comprobante dummy Pillow en memoria
                archivo = _comprobante_dummy(referencia)
                pago.comprobante.save(
                    f'seed_{referencia}.png',
                    archivo,
                    save=False,
                )

                if estado in ('APROBADO', 'RECHAZADO'):
                    pago.revisado_por = user_tes
                    pago.revisado_en = _datetime_pasado(1, 30)

                if estado == 'RECHAZADO':
                    pago.motivo_rechazo = random.choice(MOTIVOS_RECHAZO)

                pago.save()  # monto_usd y comprobante_hash se calculan aquí

                # Vincular mensualidades y audit log
                if estado == 'APROBADO':
                    for m in grupo:
                        m.pagada = True
                        m.pago = pago
                        m.save()
                    pago.registrar_audit(
                        'APROBADO',
                        actor=user_tes,
                        estado_anterior='PENDIENTE',
                        estado_nuevo='APROBADO',
                        detalles={'seed': True, 'mensualidades': [m.id for m in grupo]},
                    )
                    contadores['pagos_aprobados'] += 1
                elif estado == 'PENDIENTE':
                    pago.registrar_audit(
                        'CREADO',
                        actor=None,
                        estado_anterior='',
                        estado_nuevo='PENDIENTE',
                        detalles={'seed': True},
                    )
                    contadores['pagos_pendientes'] += 1
                else:  # RECHAZADO
                    pago.registrar_audit(
                        'RECHAZADO',
                        actor=user_tes,
                        estado_anterior='PENDIENTE',
                        estado_nuevo='RECHAZADO',
                        detalles={'seed': True, 'motivo': pago.motivo_rechazo},
                    )
                    contadores['pagos_rechazados'] += 1

                self._log(
                    f'  ✓ Pago {referencia}: {estado} | '
                    f'Bs {monto_bs} | Rep. {rep.nombres}'
                )

        # ── 14. Partidos ─────────────────────────────────────────────────
        self._log('  ⚙️  Creando partidos...', always=True)
        tipos = ['AMISTOSO', 'OFICIAL']
        condiciones = ['CASA', 'VISITANTE']
        resultados = ['VICTORIA', 'EMPATE', 'DERROTA']

        partidos_seed = []
        for i in range(1, 6):
            cat = categorias[i % n_cats]
            rival = f"[SEED] {random.choice(EQUIPOS_RIVALES)}"
            tipo = random.choice(tipos)
            condicion = random.choice(condiciones)
            gf = random.randint(0, 5)
            gc = random.randint(0, 5)
            if gf > gc:
                resultado = 'VICTORIA'
            elif gf == gc:
                resultado = 'EMPATE'
            else:
                resultado = 'DERROTA'

            dias_pasados = random.randint(7, 300)
            fecha_hora = timezone.now() - datetime.timedelta(days=dias_pasados)

            partido, creado = Partido.objects.get_or_create(
                equipo_rival=rival,
                fecha_hora__date=(timezone.now() - datetime.timedelta(days=dias_pasados)).date(),
                defaults={
                    'categoria': cat,
                    'fecha_hora': fecha_hora,
                    'tipo': tipo,
                    'condicion': condicion,
                    'goles_favor_escuela': gf,
                    'goles_contra_rival': gc,
                    'resultado': resultado,
                    'procesado': True,
                },
            )
            partidos_seed.append(partido)
            if creado:
                contadores['partidos'] += 1
                self._log(
                    f'  ✓ Partido {i}: vs {rival} | {resultado} {gf}-{gc} | {cat.nombre}'
                )

        # ── 15. Estadísticas ─────────────────────────────────────────────
        self._log('  ⚙️  Creando estadísticas...', always=True)
        for partido in partidos_seed:
            # Tomar atletas de la categoría del partido
            atletas_cat = [a for a in atletas if a.categoria_id == partido.categoria_id and a.activo]
            if not atletas_cat:
                atletas_cat = [a for a in atletas if a.activo]

            muestra = atletas_cat[:min(15, len(atletas_cat))]
            random.shuffle(muestra)

            for atleta in muestra[:10]:
                if Estadistica.objects.filter(atleta=atleta, partido=partido).exists():
                    continue
                es_titular = random.random() > 0.3
                minutos = random.randint(45, 90) if es_titular else random.randint(1, 44)
                goles = random.randint(0, 3)
                asistencias = random.randint(0, 2)
                amarillas = random.randint(0, 2)
                rojas = random.randint(0, 1)
                calificacion = random.randint(4, 10)

                Estadistica.objects.create(
                    atleta=atleta,
                    partido=partido,
                    es_titular=es_titular,
                    minutos_jugados=minutos,
                    goles=goles,
                    asistencias=asistencias,
                    tarjetas_amarillas=amarillas,
                    tarjetas_rojas=rojas,
                    calificacion_dt=calificacion,
                )
                contadores['estadisticas'] += 1
                self._log(
                    f'  ✓ Estadística: {atleta.nombres} en partido vs '
                    f'{partido.equipo_rival} | {goles}G {asistencias}A'
                )

        # ── 16. EvaluacionTecnica ─────────────────────────────────────────
        self._log('  ⚙️  Creando evaluaciones técnicas...', always=True)
        atletas_activos = [a for a in atletas if a.activo]
        random.shuffle(atletas_activos)
        for i, atleta in enumerate(atletas_activos[:10]):
            entrenador = entrenadores[i % len(entrenadores)]
            fecha_eval = _fecha_pasada(7, 180)
            EvaluacionTecnica.objects.get_or_create(
                atleta=atleta,
                fecha_evaluacion=fecha_eval,
                defaults={
                    'entrenador': entrenador,
                    'velocidad': random.randint(5, 10),
                    'resistencia': random.randint(5, 10),
                    'control_balon': random.randint(4, 10),
                    'pase_corto': random.randint(4, 10),
                    'tiro': random.randint(4, 10),
                    'inteligencia_tactica': random.randint(5, 10),
                    'observaciones': random.choice(OBSERVACIONES_TECNICAS),
                },
            )
            contadores['evaluaciones_tecnicas'] += 1
            self._log(f'  ✓ EvalTécnica #{i+1}: {atleta.nombres}')

        # ── 17. EvaluacionPsicosocial ─────────────────────────────────────
        self._log('  ⚙️  Creando evaluaciones psicosociales...', always=True)
        random.shuffle(atletas_activos)
        for i, atleta in enumerate(atletas_activos[:10]):
            fecha_eval = _fecha_pasada(7, 180)
            EvaluacionPsicosocial.objects.get_or_create(
                atleta=atleta,
                fecha_evaluacion=fecha_eval,
                defaults={
                    'coordinador_evaluador': coord_deportivo,
                    'compromiso': random.randint(5, 10),
                    'puntualidad': random.randint(5, 10),
                    'companerismo': random.randint(6, 10),
                    'respeto': random.randint(6, 10),
                    'manejo_frustracion': random.randint(4, 10),
                    'observaciones_conductuales': random.choice(OBSERVACIONES_PSICOSOCIALES),
                },
            )
            contadores['evaluaciones_psicosociales'] += 1
            self._log(f'  ✓ EvalPsicosocial #{i+1}: {atleta.nombres}')

        # ── Resumen final ─────────────────────────────────────────────────
        total_pagos = (
            contadores['pagos_aprobados']
            + contadores['pagos_pendientes']
            + contadores['pagos_rechazados']
        )
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('✓ Seed FDM completado'))
        self.stdout.write('  - 1 superuser')
        self.stdout.write(f"  - {contadores['coordinadores']} coordinadores")
        self.stdout.write(f"  - {contadores['tesoreria']} tesorería")
        self.stdout.write(f"  - {contadores['entrenadores']} entrenadores")
        self.stdout.write(f"  - {contadores['delegados']} delegados")
        self.stdout.write(f"  - {contadores['categorias']} categorías")
        self.stdout.write(f"  - {contadores['representantes']} representantes")
        self.stdout.write(
            f"  - {contadores['atletas']} atletas "
            f"({contadores['atletas_becados']} becados, "
            f"{contadores['atletas_inactivos']} inactivos)"
        )
        self.stdout.write(
            f"  - {contadores['mensualidades']} mensualidades (3 meses)"
        )
        self.stdout.write(
            f"  - {total_pagos} pagos "
            f"({contadores['pagos_aprobados']} aprobados, "
            f"{contadores['pagos_pendientes']} pendientes, "
            f"{contadores['pagos_rechazados']} rechazados)"
        )
        self.stdout.write(f"  - {contadores['tasa_bcv']} TasaBCV")
        self.stdout.write(
            f"  - {contadores['partidos']} partidos, "
            f"{contadores['estadisticas']} estadísticas"
        )
        self.stdout.write(f"  - {contadores['evaluaciones_tecnicas']} evaluaciones técnicas")
        self.stdout.write(f"  - {contadores['evaluaciones_psicosociales']} evaluaciones psicosociales")
        self.stdout.write('')
        self.stdout.write(self.style.WARNING('Credenciales demo:'))
        self.stdout.write(f"  Superuser:             admin_seed / {self._password}")
        self.stdout.write(f"  Coordinador General:   seed_coord_general / {self._password}")
        self.stdout.write(f"  Coordinador Deportivo: seed_coord_deportivo / {self._password}")
        self.stdout.write(f"  Tesorería:             seed_tesoreria / {self._password}")
        self.stdout.write(f"  Representante ejemplo: seed_rep_001 / {self._password}")

    # ──────────────────────────────────────────
    # Helper de logging
    # ──────────────────────────────────────────

    def _log(self, mensaje, always=False):
        """Imprime si --verbose o always=True."""
        if self._verbose or always:
            self.stdout.write(mensaje)
