# finanzas/management/commands/generar_mensualidades.py
import calendar
from datetime import date
from decimal import Decimal
from django.core.management.base import BaseCommand
from django.utils import timezone
from filiacion.models import Atleta
from finanzas.models import Mensualidad


# Monto por defecto si el atleta/categoría no define uno propio
MONTO_DEFAULT_USD = Decimal('15.00')


class Command(BaseCommand):
    help = 'Genera mensualidades para todos los atletas activos del mes especificado.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--mes', type=int, default=None,
            help='Mes (1-12). Default: mes actual.'
        )
        parser.add_argument(
            '--anio', type=int, default=None,
            help='Año. Default: año actual.'
        )
        parser.add_argument(
            '--monto', type=str, default=None,
            help=f'Monto USD. Default: {MONTO_DEFAULT_USD} o el de la categoría.'
        )
        parser.add_argument(
            '--dia-vencimiento', type=int, default=10,
            help='Día del mes en que vence. Default: 10.'
        )

    def handle(self, *args, **opts):
        hoy = timezone.now().date()
        mes = opts['mes'] or hoy.month
        anio = opts['anio'] or hoy.year
        dia_venc = opts['dia_vencimiento']
        monto_override = Decimal(opts['monto']) if opts['monto'] else None

        # Validar día de vencimiento contra el mes
        ultimo_dia = calendar.monthrange(anio, mes)[1]
        dia_venc = min(dia_venc, ultimo_dia)
        fecha_venc = date(anio, mes, dia_venc)

        atletas = Atleta.objects.filter(activo=True).exclude(becado=True)

        creadas = 0
        existentes = 0

        for atleta in atletas:
            # Determinar monto: parámetro CLI > monto de categoría (si existe) > default
            if monto_override is not None:
                monto = monto_override
            else:
                # Si Categoria tiene campo de monto, usarlo. Si no, default.
                # Decisión técnica: Categoria no tiene monto_mensualidad_usd actualmente,
                # se usa getattr como fallback seguro para compatibilidad futura.
                monto = getattr(atleta.categoria, 'monto_mensualidad_usd', None) or MONTO_DEFAULT_USD

            mensualidad, created = Mensualidad.objects.get_or_create(
                atleta=atleta,
                periodo_mes=mes,
                periodo_anio=anio,
                defaults={
                    'monto_usd': monto,
                    'fecha_vencimiento': fecha_venc,
                }
            )
            if created:
                creadas += 1
            else:
                existentes += 1

        self.stdout.write(self.style.SUCCESS(
            f'Mensualidades {mes}/{anio}: {creadas} creadas, {existentes} ya existían.'
        ))
